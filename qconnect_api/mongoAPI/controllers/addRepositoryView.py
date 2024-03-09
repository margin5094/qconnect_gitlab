from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mongoAPI.services.addRespositoryService import add_repository
from mongoAPI.controllers.queue import send_task_to_queue

class RepositoryAPIView(APIView):
    def post(self, request):
        repository_id = request.data.get('repositoryId')
        repository_name = request.data.get('repositoryName')
        userId='f4613ff9-8160-48f9-af20-5dc03c051e7f'
        
        # Basic validation
        if not repository_id or not repository_name:
            return Response({'error': 'Missing repositoryId or repositoryName'}, status=status.HTTP_400_BAD_REQUEST)

        task_data = {
            'repository_ids': [repository_id],
            'userId': userId
        }
        send_task_to_queue(task_data)
        
        try:
            add_repository(userId, repository_name,repository_id)
            return Response({'repositoryId': 'Repository added successfully!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Handle exceptions raised by the service or model layer
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

