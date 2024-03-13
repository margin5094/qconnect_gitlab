from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from mongoAPI.models.RepositoryModel import Repository
from mongoAPI.controllers.queue import send_task_to_queue
from mongoAPI.services.functionService import fetch_and_store_merge_requests, fetch_and_store_commits, fetch_and_store_gitlab_projects
from mongoAPI.services.synchronizeService import get_refresh_token_by_id, get_new_accessToken

class RefreshTokenActionAPIView(APIView):
    def post(self, request):
        userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        
        repository = Repository.objects.get(userId=userId)
        repo_ids = list(repository.repoIds.keys())

        task_data = {
            'repository_ids': repo_ids,
            'userId': userId
        }
        # -------------------------------------------------------------------------
        # repository_ids = task_data['repository_ids'] 
        # refresh_token = get_refresh_token_by_id(token_id=userId)
        # result = get_new_accessToken(refresh_token,token_id=userId)
        # access_token = result['access_token']

        # for repository_id in repository_ids:  # Loop over each repository ID
    
        #     fetch_and_store_commits(repository_id=repository_id, access_token=access_token)
        
        # -------------------------------------------------------------------------
        send_task_to_queue(task_data)
        result = {
            'status': 'success',
            'message': 'Synchronization completed successfully.'
            }
            
        return JsonResponse(result)
