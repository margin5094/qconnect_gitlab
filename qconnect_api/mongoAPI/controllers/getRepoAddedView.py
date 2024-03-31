# Importing necessary components
from django.http import JsonResponse
from rest_framework.views import APIView
from mongoAPI.models.RepositoryModel import Repository
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class GetAddedRepoView(APIView):
    # Decorating the get method with Swagger auto schema for documentation
    @swagger_auto_schema(
        # Defining response schema for Swagger documentation
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                        "repoIds": openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: "Repository not found"
        }
    )

    # Handling HTTP GET requests
    def get(self, request):
        # Defining the userId
        userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        try:
            # Querying the Repository model for the repository associated with the provided userId
            repository = Repository.objects.get(userId=userId)
            # Constructing response data
            response_data = {
                'status': 'success',
                'repoIds': repository.repoIds
            }
        except Repository.DoesNotExist:
            # Returning an error response if the repository is not found for the provided userId
            return JsonResponse({'status': 'error', 'message': 'Repository not found'}, status=404)
        
        # Returning JSON response with the retrieved repository information
        return JsonResponse(response_data)
