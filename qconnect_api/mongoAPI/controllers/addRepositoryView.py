from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Importing necessary functions from services and controllers
from mongoAPI.services.addRespositoryService import add_repository
from mongoAPI.controllers.queue import send_task_to_queue
# Importing necessary components from drf_yasg for Swagger documentation
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class RepositoryAPIView(APIView):
    # Decorating the post method with Swagger auto schema for documentation
    @swagger_auto_schema(
        # Defining the request body schema for Swagger documentation
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['repositoryId', 'repositoryName'],
            properties={
                'repositoryId': openapi.Schema(type=openapi.TYPE_STRING),
                'repositoryName': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        # Defining the response schema for Swagger documentation
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

    # Handling HTTP POST requests
    def post(self, request):
        # Extracting repositoryId and repositoryName from the request data
        repository_id = request.data.get('repositoryId')
        repository_name = request.data.get('repositoryName')
        userId='f4613ff9-8160-48f9-af20-5dc03c051e7f'
        
        # Checking if repositoryId or repositoryName is missing
        if not repository_id or not repository_name:
            return Response({'error': 'Missing repositoryId or repositoryName'}, status=status.HTTP_400_BAD_REQUEST)

        # Constructing task data to be sent to the queue
        task_data = {
            'repository_ids': [repository_id],
            'userId': userId
        }
        
        try:
            # Calling service function to add repository to the database
            add_repository(userId, repository_name,repository_id)
            # Sending task data to the queue for further processing
            send_task_to_queue(task_data)
            # Returning success response
            return Response({'repositoryId': 'Repository added successfully!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Returning error response in case of any exception
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
