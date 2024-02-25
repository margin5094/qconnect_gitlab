import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Repository

class RepositoryInfoAPIView(APIView):
    def get(self, request):
        # Extract access token from the header
        access_token = request.headers.get('Authorization')
        print(f'access token: {access_token}')
        # GitLab API endpoint for listing repositories
        gitlab_api_url = 'https://git.cs.dal.ca/api/v4/projects'
        params = {'owned': 'yes'}
        # Set up headers for the GitLab API request
        headers = {
            'Authorization': f'{access_token}',
        }

        try:
            # Make a request to GitLab API to fetch repositories
            response = requests.get(gitlab_api_url, headers=headers, params=params)
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the JSON response from GitLab
                repositories_data = response.json()
                # print(f'Response: {repositories_data}')
                
                
                return Response(repositories_data, status=status.HTTP_200_OK)
                
            else:
                # Return an error response if the GitLab API request was not successful
                return Response({'error': 'Failed to fetch repository information from GitLab'}, status=response.status_code)

        except Exception as e:
            # Handle exceptions, such as network errors or invalid JSON response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
