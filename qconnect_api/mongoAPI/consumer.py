import pika
import json
import pika
import json
from mongoAPI.services.functionService import fetch_and_store_merge_requests, fetch_and_store_commits
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Starts the RabbitMQ consumer'

    def handle(self, *args, **options):
        def callback(ch, method, properties, body):
            task_data = json.loads(body)
            repository_id = task_data['repository_id']
            access_token = task_data['access_token']
            print(f'{repository_id}')
            fetch_and_store_merge_requests(repository_id=repository_id, access_token=access_token)
            fetch_and_store_commits(repository_id=repository_id, access_token=access_token)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='task_queue', on_message_callback=callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
