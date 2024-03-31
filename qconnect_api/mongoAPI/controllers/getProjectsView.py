from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Importing the Project model
from mongoAPI.models.ProjectsModel import Project
# Importing necessary components from drf_yasg for Swagger documentation
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class ReposForUserView(APIView):
    # Decorating the get method with Swagger auto schema for documentation
    @swagger_auto_schema(
        # Defining response schema for Swagger documentation
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                )
            ),
            404: "Project not found for the provided userId"
        }
    )

    # Handling HTTP GET requests
    def get(self, request):
        # Defining the userId
        userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        try:
            # Querying the Project model for the project associated with the provided userId
            project = Project.objects.get(userId=userId)
            # Returning the repositories associated with the project
            return Response(project.repos)
        except Project.DoesNotExist:
            # Returning an error response if the project is not found for the provided userId
            return Response({"error": "Project not found for the provided userId."}, status=status.HTTP_404_NOT_FOUND)
