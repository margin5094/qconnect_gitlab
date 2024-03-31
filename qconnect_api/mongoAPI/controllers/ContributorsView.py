from django.http import JsonResponse
from rest_framework.views import APIView
# Importing necessary functions from services
from mongoAPI.services.ContributorsService import get_unique_contributors_count, get_contributors_data, get_top_active_contributors
from rest_framework.response import Response
from rest_framework import status
# Importing necessary components from drf_yasg for Swagger documentation
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class ActiveSumContributorsView(APIView):
    # Decorating the post method with Swagger auto schema for documentation
    @swagger_auto_schema(
        # Defining manual parameters for Swagger documentation
        manual_parameters=[
            openapi.Parameter(
                name='startDate',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Start date for the range of activity (format: YYYY-MM-DD)'
            ),
            openapi.Parameter(
                name='endDate',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='End date for the range of activity (format: YYYY-MM-DD)'
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
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: "Missing required parameters"
        }
    )

    # Handling HTTP POST requests
    def post(self, request):
        # Extracting parameters from the query string
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        repository_ids = request.query_params.getlist('repositoryIds')

        # Checking if any required parameters are missing
        if not start_date or not end_date or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calling service function to get unique contributors count
        count = get_unique_contributors_count(start_date, end_date, repository_ids)
        # Returning JSON response
        return JsonResponse({'count': count})

class ActiveContributorsView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='startDate',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Start date for the range of activity (format: YYYY-MM-DD)'
            ),
            openapi.Parameter(
                name='endDate',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='End date for the range of activity (format: YYYY-MM-DD)'
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
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "dates": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING)
                            ),
                            "activeUsers": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_INTEGER)
                            ),
                            "totalUsers": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_INTEGER)
                            )
                        }
                    )
                )
            ),
            400: "Missing required parameters"
        }
    )

    def post(self, request, *args, **kwargs):
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        repository_ids = request.query_params.getlist('repositoryIds')

        if not start_date or not end_date or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=400)

        data = get_contributors_data(start_date, end_date, repository_ids)
        return Response(data)
    
class TopActiveContributorsView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='startDate',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Start date for the range of activity (format: YYYY-MM-DD)'
            ),
            openapi.Parameter(
                name='endDate',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='End date for the range of activity (format: YYYY-MM-DD)'
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
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "email": openapi.Schema(type=openapi.TYPE_STRING),
                            "commits": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "name": openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            ),
            400: "Missing required parameters"
        }
    )

    def post(self, request, *args, **kwargs):
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        repository_ids = request.query_params.getlist('repositoryIds')

        if not start_date or not end_date or not repository_ids:
            return Response({"error": "Missing required parameters"}, status=400)

        top_contributors = get_top_active_contributors(start_date, end_date, repository_ids)
        return Response(top_contributors)
