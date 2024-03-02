from rest_framework.views import APIView
from rest_framework.response import Response
from mongoAPI.services.MergeRequestService import MergeRequestService

class PRActiveNew(APIView):
    def post(self, request):
        start_date_str = request.query_params.get('startDate', None)
        end_date_str = request.query_params.get('endDate', None)
        repository_ids = request.query_params.getlist('repositoryIds', [])

        if not start_date_str or not end_date_str or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=400)

        total_merge_requests = MergeRequestService.get_active_and_new_prs(start_date_str, end_date_str, repository_ids)

        return Response(total_merge_requests)

class PRAvgTimeClose(APIView):
    def post(self, request):
        start_date_str = request.query_params.get('startDate', None)
        end_date_str = request.query_params.get('endDate', None)
        repository_ids = request.query_params.getlist('repositoryIds', [])

        if not start_date_str or not end_date_str or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=400)

        avg_time_to_close = MergeRequestService.get_avg_time_to_close(start_date_str, end_date_str, repository_ids)

        return Response(avg_time_to_close)