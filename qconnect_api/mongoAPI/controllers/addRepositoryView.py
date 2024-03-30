from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mongoAPI.services.addRespositoryService import add_repository
from mongoAPI.controllers.queue import send_task_to_queue
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class RepositoryAPIView(APIView):
    @swagger_auto_schema(
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['repositoryId', 'repositoryName'],
            properties={
                'repositoryId': openapi.Schema(type=openapi.TYPE_STRING),
                'repositoryName': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: openapi.Response(description="Repository added successfully!", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'repositoryId': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: "Missing repositoryId or repositoryName",
            500: "Internal Server Error"
        }
    )

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
        
        try:
            add_repository(userId, repository_name,repository_id)
            send_task_to_queue(task_data)
            return Response({'repositoryId': 'Repository added successfully!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Handle exceptions raised by the service or model layer
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

