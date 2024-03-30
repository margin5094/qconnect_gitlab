from rest_framework.views import APIView
from rest_framework.response import Response
from mongoAPI.services.MergeRequestService import MergeRequestService
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class PRActiveNew(APIView):
    @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name='startDate',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Start date for the range of merge requests (format: YYYY-MM-DD)'
        ),
        openapi.Parameter(
            name='endDate',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='End date for the range of merge requests (format: YYYY-MM-DD)'
        ),
        openapi.Parameter(
            name='repositoryIds',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            required=True,
            description='List of repository IDs'
        )
    ],
    responses={
        200: openapi.Response(
            description="Successful response",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "dates": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING)
                    ),
                    "active": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_INTEGER)
                    ),
                    "newly_created": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_INTEGER)
                    )
                }
            )
        ),
        400: "Missing required parameters"
        }
    )

    def post(self, request):
        start_date_str = request.query_params.get('startDate', None)
        end_date_str = request.query_params.get('endDate', None)
        repository_ids = request.query_params.getlist('repositoryIds', [])

        if not start_date_str or not end_date_str or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=400)

        total_merge_requests = MergeRequestService.get_active_and_new_prs(start_date_str, end_date_str, repository_ids)

        return Response(total_merge_requests)

class PRAvgTimeClose(APIView):
    @swagger_auto_schema(
    manual_parameters=[
            openapi.Parameter(
                name='startDate',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Start date for the range of merge requests (format: YYYY-MM-DD)'
            ),
            openapi.Parameter(
                name='endDate',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='End date for the range of merge requests (format: YYYY-MM-DD)'
            ),
            openapi.Parameter(
                name='repositoryIds',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                required=True,
                description='List of repository IDs'
            )
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "dates": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        "times": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
                        )
                    }
                )
            ),
            400: "Missing required parameters"
        }
    )

    def post(self, request):
        start_date_str = request.query_params.get('startDate', None)
        end_date_str = request.query_params.get('endDate', None)
        repository_ids = request.query_params.getlist('repositoryIds', [])

        if not start_date_str or not end_date_str or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=400)

        avg_time_to_close = MergeRequestService.get_avg_time_to_close(start_date_str, end_date_str, repository_ids)

        return Response(avg_time_to_close)