import requests
from .models import Repository

class RepositoryService:
    @staticmethod
    def get_gitlab_repositories(access_token):
        gitlab_api_url = 'https://git.cs.dal.ca/api/v4/projects'
        params = {'owned': 'yes'}
        headers = {'Authorization': f'{access_token}'}

        try:
            response = requests.get(gitlab_api_url, headers=headers, params=params)

            if response.status_code == 200:
                repositories_data = response.json()
                return repositories_data
            else:
                raise Exception(f'Failed to fetch repository information from GitLab. Status code: {response.status_code}')

        except Exception as e:
            raise e

    @staticmethod
    def add_repository(repository_id, access_token):
        try:
            # Fetch repository information from GitLab API
            repository_info = RepositoryService.get_gitlab_repository_info(repository_id, access_token)

            # Create or update the repository in the MongoDB collection
            repository, created = Repository.objects.update_or_create(
                id=repository_id,
                defaults={
                    'id': repository_id,
                    'name': repository_info.get('name', ''),
                    'description': repository_info.get('description', ''),
                    # Add other fields as needed based on the GitLab API response
                }
            )

            return {'message': f'Repository with ID {repository_id} added successfully.'}

        except Exception as e:
            raise e
        
    @staticmethod
    def get_gitlab_repository_info(repository_id, access_token):
        gitlab_api_url = f'https://git.cs.dal.ca/api/v4/projects/{repository_id}'
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(gitlab_api_url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'Failed to fetch repository information from GitLab. Status code: {response.status_code}')

        except Exception as e:
            raise e
