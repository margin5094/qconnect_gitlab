from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import RepositoryService

class RepositoryInfoAPIView(APIView):
    def get(self, request):
        access_token = request.headers.get('Authorization')

        try:
            repositories_data = RepositoryService.get_gitlab_repositories(access_token)
            return Response(repositories_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AddRepositoryAPIView(APIView):
    def post(self, request):
        repository_id = request.data.get('id')
        access_token = request.data.get('access_token')

        if not repository_id or not access_token:
            return Response({'error': 'Repository ID and access token are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = RepositoryService.add_repository(repository_id, access_token)
            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
