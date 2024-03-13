# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mongoAPI.models.ProjectsModel import Project

class ReposForUserView(APIView):
    def get(self, request):
        userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        try:
            print(f'called!')
            project = Project.objects.get(userId=userId)
            
            return Response(project.repos)
        except Project.DoesNotExist:
            return Response({"error": "Project not found for the provided userId."}, status=status.HTTP_404_NOT_FOUND)
