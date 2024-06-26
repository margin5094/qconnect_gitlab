from rest_framework.views import APIView
from rest_framework.response import Response
from mongoAPI.services.MergeRequestService import MergeRequestService
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class PRActiveNew(APIView):
    # Decorating the post method with Swagger auto schema for documentation
    @swagger_auto_schema(
        # Defining manual parameters for Swagger documentation
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
        # Defining response schema for Swagger documentation
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

    # Handling HTTP POST requests
    def post(self, request):
        # Extracting parameters from the query string
        start_date_str = request.query_params.get('startDate', None)
        end_date_str = request.query_params.get('endDate', None)
        repository_ids = request.query_params.getlist('repositoryIds', [])

        # Checking if any required parameters are missing
        if not start_date_str or not end_date_str or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=400)

        # Calling service function to get active and newly created PRs
        total_merge_requests = MergeRequestService.get_active_and_new_prs(start_date_str, end_date_str, repository_ids)

        # Returning response
        return Response(total_merge_requests)

class PRAvgTimeClose(APIView):
    # Decorating the post method with Swagger auto schema for documentation
    @swagger_auto_schema(
        # Defining manual parameters for Swagger documentation
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
        # Defining response schema for Swagger documentation
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

    # Handling HTTP POST requests
    def post(self, request):
        # Extracting parameters from the query string
        start_date_str = request.query_params.get('startDate', None)
        end_date_str = request.query_params.get('endDate', None)
        repository_ids = request.query_params.getlist('repositoryIds', [])

        # Checking if any required parameters are missing
        if not start_date_str or not end_date_str or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=400)

        # Calling service function to get average time to close PRs
        avg_time_to_close = MergeRequestService.get_avg_time_to_close(start_date_str, end_date_str, repository_ids)

        # Returning response
        return Response(avg_time_to_close)
