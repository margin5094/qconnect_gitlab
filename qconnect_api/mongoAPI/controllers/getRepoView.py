# Assuming you are using Django REST Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mongoAPI.models.tokenModel import Token
from mongoAPI.services.getRepoService import fetch_gitlab_projects

class GitLabProjectsView(APIView):

    def get(self, request):
        user_id = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        try:
            token = Token.objects.get(id=user_id) 
            # print(f"{token.access_token}")
            projects = fetch_gitlab_projects(token.access_token)
            return Response(projects)
        except Token.DoesNotExist:
            return Response({'error': 'Token not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
