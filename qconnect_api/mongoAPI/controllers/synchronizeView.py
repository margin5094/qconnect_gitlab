from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from mongoAPI.models.RepositoryModel import Repository
from mongoAPI.controllers.queue import send_task_to_queue
from mongoAPI.services.functionService import fetch_and_store_merge_requests, fetch_and_store_commits, fetch_and_store_gitlab_projects
from mongoAPI.services.synchronizeService import get_refresh_token_by_id, get_new_accessToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RefreshTokenActionAPIView(APIView):
    @swagger_auto_schema(
        request_body=None,
        responses={
            200: openapi.Response('Synchronization completed successfully.'),
            404: openapi.Response('Repository not found'),
        }
    )
    def post(self, request):
        userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        
        try:
            repository = Repository.objects.get(userId=userId)
            repo_ids = list(repository.repoIds.keys())

            task_data = {
                'repository_ids': repo_ids,
                'userId': userId
            }

            send_task_to_queue(task_data)
            result = {
                'status': 'success',
                'message': 'Synchronization completed successfully.'
            }
        except Repository.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Repository not found'}, status=404)
            
        return JsonResponse(result)
