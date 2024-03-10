from django.http import JsonResponse
from rest_framework.views import APIView
from mongoAPI.models.RepositoryModel import Repository

class GetAddedRepoView(APIView):
   
    def get(self, request):
        userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        try:
            repository = Repository.objects.get(userId=userId)
            response_data = {
                'status': 'success',
                'repoIds': repository.repoIds
            }
        except Repository.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Repository not found'}, status=404)
        
        return JsonResponse(response_data)
