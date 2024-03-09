import pika
import json
import os

#-----------------rabbitMQ task producer----------------
def send_task_to_queue(task_data):
    # connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    url = os.getenv('CLOUDAMQP_URL')
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=json.dumps(task_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))

    connection.close()