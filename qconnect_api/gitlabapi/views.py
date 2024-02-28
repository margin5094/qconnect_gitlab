from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import RepositoryService, GitUserService, GitLabService
from datetime import datetime

class RepositoryInfoAPIView(APIView):
    def get(self, request):
        access_token = request.headers.get('Authorization')

        try:
            repositories_data = RepositoryService.get_gitlab_repositories(access_token)
            return Response(repositories_data, status=status.HTTP_200_OK)

        except Exception as e: 
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AddRepositoryAPIView(APIView):
    def post(self, request):
        repository_id = request.data.get('id')
        access_token = request.headers.get('Authorization')

        if not repository_id or not access_token:
            return Response({'error': 'Repository ID and access token are required in the request.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = RepositoryService.add_repository(repository_id, access_token)
            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TopGitUsersAPIView(APIView):
    def post(self, request):
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        repository_ids = request.query_params.getlist('repositoryIds')
        access_token = request.headers.get('Authorization')
        print(f"{repository_ids}")
        try:
            # Call a service method to fetch top 5 git users
            top_git_users = GitUserService.get_top_git_users(start_date, end_date, repository_ids,access_token)

            return Response(top_git_users, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActiveContributorsCountAPIView(APIView):
    def post(self, request):
        start_date_str = request.query_params.get('startDate')
        end_date_str = request.query_params.get('endDate')
        repository_ids = request.query_params.getlist('repositoryIds')
        print(f"{repository_ids}")
        if not (start_date_str and end_date_str and repository_ids):
            return Response({'error': 'startDate, endDate, and repositoryIds are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%d-%m')
            end_date = datetime.strptime(end_date_str, '%Y-%d-%m')

            # Format datetime objects to the desired output format
            start_date_formatted = start_date.strftime('%Y-%m-%dT00:00:00.000Z')
            end_date_formatted = end_date.strftime('%Y-%m-%dT00:00:00.000Z')

            access_token = request.headers.get('Authorization')
            count = GitLabService.get_active_contributors_count(repository_ids, start_date_formatted, end_date_formatted, access_token)
            
            return Response({'count': count}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GitUsersActiveAPIView(APIView):
    def post(self, request):
        start_date_str = request.query_params.get('startDate')
        end_date_str = request.query_params.get('endDate')
        repository_ids = request.query_params.getlist('repositoryIds')

        if not (start_date_str and end_date_str and repository_ids):
            return Response({'error': 'startDate, endDate, and repositoryIds are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:

            start_date = datetime.strptime(start_date_str, '%Y-%d-%m')
            end_date = datetime.strptime(end_date_str, '%Y-%d-%m')

            # Format datetime objects to the desired output format
            start_date_formatted = start_date.strftime('%Y-%m-%dT00:00:00.000Z')
            end_date_formatted = end_date.strftime('%Y-%m-%dT00:00:00.000Z')

            access_token = request.headers.get('Authorization')

            # Fetch active contributors
            active_contributors_data = GitLabService.get_active_contributors_count(repository_ids, start_date_formatted, end_date_formatted, access_token)
            # print(f'{active_contributors_data}')
            # Fetch total contributors for each date
            total_contributors_data = GitLabService.get_total_contributors_count(repository_ids, access_token)
            # print(f'{total_contributors_data}')
            # Combine the data for response
            response_data = []

            # Assuming active_contributors_data and total_contributors_data are single values
            response_data.append({
                'dates': [start_date_formatted, end_date_formatted],  # Add your desired date format
                'activeUsers': [active_contributors_data],
                'totalUsers': [total_contributors_data],
            })


            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GitUsersMergeRequestActiveAPIView(APIView):
    def post(self, request):
        try:
            access_token = request.headers.get('Authorization')
            start_date_str = request.query_params.get('startDate')
            end_date_str = request.query_params.get('endDate')
            repository_ids = request.query_params.getlist('repositoryIds')

            if not access_token or not repository_ids or not start_date_str or not end_date_str:
                return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

            start_date = datetime.strptime(start_date_str, '%Y-%d-%m')
            end_date = datetime.strptime(end_date_str, '%Y-%d-%m')

            # Format datetime objects to the desired output format
            start_date_formatted = start_date.strftime('%Y-%m-%dT00:00:00.000Z')
            end_date_formatted = end_date.strftime('%Y-%m-%dT00:00:00.000Z')


            result = GitLabService.get_active_merge_requests(access_token, repository_ids, start_date_formatted, end_date_formatted)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)