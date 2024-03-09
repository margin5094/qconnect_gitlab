from django.core.management.base import BaseCommand
import pika
import json
from mongoAPI.services.functionService import fetch_and_store_merge_requests, fetch_and_store_commits
from mongoAPI.services.synchronizeService import get_refresh_token_by_id, get_new_accessToken
import os

class Command(BaseCommand):
    help = 'Starts the RabbitMQ consumer'

    def handle(self, *args, **options):
        def callback(ch, method, properties, body):
            task_data = json.loads(body)
            repository_ids = task_data['repository_ids']  # This is now a list
            userId = task_data['userId']
            try:
                refresh_token = get_refresh_token_by_id(token_id=userId)
                result = get_new_accessToken(refresh_token,token_id=userId)
                access_token = result['access_token']
            except Exception as e: 
                print(f'Error getting refresh token!')

            for repository_id in repository_ids:  # Loop over each repository ID
                try:
                    print(f'Processing {repository_id}')
                    fetch_and_store_merge_requests(repositoryId=repository_id, access_token=access_token)
                    fetch_and_store_commits(repository_id=repository_id, access_token=access_token)
                    print(f'Successfully processed {repository_id}')
                except Exception as e:
                   
                    print(f'Error processing {repository_id}: {e}')
                    # Optionally, you could log the error to a file or another logging system

            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f'Completed processing all repository IDs for userId {userId}')

        url = os.getenv('CLOUDAMQP_URL')
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='task_queue', on_message_callback=callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
