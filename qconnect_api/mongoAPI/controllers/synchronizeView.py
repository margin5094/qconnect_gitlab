from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from mongoAPI.models.RepositoryModel import Repository
from mongoAPI.controllers.queue import send_task_to_queue

class RefreshTokenActionAPIView(APIView):
    def post(self, request):
        userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        
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
        return JsonResponse(result)
