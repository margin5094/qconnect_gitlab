from django.core.management.base import BaseCommand
import pika
import json
from mongoAPI.services.functionService import fetch_and_store_merge_requests, fetch_and_store_commits, fetch_and_store_gitlab_projects
from mongoAPI.services.synchronizeService import get_refresh_token_by_id, get_new_accessToken
import os

class Command(BaseCommand):
    # Description for the command
    help = 'Starts the RabbitMQ consumer'

    # Method to handle command execution
    def handle(self, *args, **options):
        # Define callback function to process incoming messages
        def callback(ch, method, properties, body):

            # Parse message body from JSON
            task_data = json.loads(body)

            # Extract repository IDs and user ID from the message
            repository_ids = task_data['repository_ids']  # This is now a list
            userId = task_data['userId']
            
            try:
                # Retrieve refresh token for the user
                refresh_token = get_refresh_token_by_id(token_id=userId)
                # Get a new access token using the refresh token
                result = get_new_accessToken(refresh_token,token_id=userId)
                access_token = result['access_token']

            except Exception as e: 
                # Handle errors in obtaining refresh token or access token
                print(f'Error getting refresh token: {e}')
            
            # Fetch and store GitLab projects associated with the user
            fetch_and_store_gitlab_projects(userId, access_token)
            
            # Process merge requests and commits for each repository ID
            for repository_id in repository_ids:
                try:
                    # Print message indicating processing of the repository
                    print(f'Processing {repository_id}')

                    # Fetch and store merge requests for the repository
                    fetch_and_store_merge_requests(repositoryId=repository_id, access_token=access_token)

                    # Fetch and store commits for the repository
                    fetch_and_store_commits(repository_id=repository_id, access_token=access_token)

                    # Print success message for the repository
                    print(f'Successfully processed {repository_id}')
                except Exception as e:
                    # Handle errors encountered during processing of the repository
                    print(f'Error processing {repository_id}: {e}')
                    # Optionally, log the error to a file or another logging system

            # Acknowledge message processing completion
            ch.basic_ack(delivery_tag=method.delivery_tag)

            # Print message indicating completion of processing for all repository IDs
            print(f'Completed processing all repository IDs for userId {userId}')

        # Get RabbitMQ URL from environment variable
        url = os.getenv('CLOUDAMQP_URL')
        # Establish connection to RabbitMQ server

        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # Declare the task queue with durability
        channel.queue_declare(queue='task_queue', durable=True)

        # Set prefetch count to 1 to ensure fair message distribution among consumers
        channel.basic_qos(prefetch_count=1)

        # Register the callback function to consume messages from the task queue
        channel.basic_consume(queue='task_queue', on_message_callback=callback)

        # Print message indicating consumer is waiting for messages
        print(' [*] Waiting for messages. To exit press CTRL+C')
        
        # Start consuming messages from the task queue
        channel.start_consuming()
