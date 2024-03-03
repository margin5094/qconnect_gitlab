from django.http import JsonResponse
from rest_framework.views import APIView
from mongoAPI.services.ContributorsService import get_unique_contributors_count
from rest_framework.response import Response
from rest_framework import status

class ActiveSumContributorsView(APIView):
    def post(self, request):
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        repository_ids = request.query_params.getlist('repositoryIds')

        if not start_date or not end_date or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        count = get_unique_contributors_count(start_date, end_date, repository_ids)
        return JsonResponse({'count': count})
