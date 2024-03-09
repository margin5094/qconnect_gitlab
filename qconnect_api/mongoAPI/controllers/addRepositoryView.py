from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mongoAPI.services.addRespositoryService import add_repository
# from mongoAPI.services.functionService import fetch_and_store_merge_requests, fetch_and_store_commits
from mongoAPI.services.synchronizeService import get_refresh_token_by_id, get_new_accessToken
from django.http import JsonResponse
import pika
import json

class RepositoryAPIView(APIView):
    
    def post(self, request):
        repository_id = request.data.get('repositoryId')
        repository_name = request.data.get('repositoryName')
        userId='f4613ff9-8160-48f9-af20-5dc03c051e7f'
        
        # Basic validation
        if not repository_id or not repository_name:
            return Response({'error': 'Missing repositoryId or repositoryName'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get refresh token by ID
        refresh_token = get_refresh_token_by_id(token_id=userId)
        if refresh_token is None:
            return JsonResponse({"error": "Token not found"}, status=404)
        # Perform your custom logic with the refresh token
        result = get_new_accessToken(refresh_token,token_id=userId)
        access_token=result['access_token']

        task_data = {
            'repository_id': repository_id,
            'access_token': access_token
        }
        self.send_task_to_queue(task_data)
        
        
        try:
            add_repository(userId, repository_name,repository_id)
            return Response({'repositoryId': 'Repository added successfully!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Handle exceptions raised by the service or model layer
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#-----------------rabbitMQ task producer----------------

    def send_task_to_queue(self,task_data):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
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