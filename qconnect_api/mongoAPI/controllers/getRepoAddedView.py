from django.http import JsonResponse
from rest_framework.views import APIView
from mongoAPI.models.RepositoryModel import Repository
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
class GetAddedRepoView(APIView):
    @swagger_auto_schema(
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
