import requests
from .models import Repository
from .models import Commit
from datetime import datetime

class RepositoryService:
    @staticmethod
    def get_gitlab_repositories(access_token):
        gitlab_api_url = 'https://git.cs.dal.ca/api/v4/projects'
        params = {'membership': 'true'}
        headers = {'Authorization': f'{access_token}'}

        try:
            response = requests.get(gitlab_api_url, headers=headers, params=params)

            if response.status_code == 200:
                repositories_data = response.json()

                # Extract only 'id' and 'name' from each repository
                filtered_repositories = [{'id': repo['id'], 'name': repo['name']} for repo in repositories_data]

                return filtered_repositories
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
        headers = {'Authorization': f'{access_token}'}

        try:
            response = requests.get(gitlab_api_url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'Failed to fetch repository information from GitLab. Status code: {response.status_code}')

        except Exception as e:
            raise e


class GitUserService:
    @staticmethod
    def get_top_git_users(start_date, end_date, repository_ids, access_token):
        try:
            # Initialize an empty list to store user details
            top_git_users = []

            # Loop through repository IDs and fetch GitLab data
            for repo_id in repository_ids:
                repo_contributors = GitUserService.get_repository_details(repo_id, access_token)
                top_git_users.extend(GitUserService.get_top_users_from_repo(repo_contributors, start_date, end_date))

            # Limit the result to the top 5 users
            top_git_users = sorted(top_git_users, key=lambda x: x['commits'], reverse=True)[:5]

            return top_git_users

        except Exception as e:
            raise e

    @staticmethod
    def get_repository_details(repo_id, access_token):
        # Use the GitLab API to get details of contributors for a specific repository
        gitlab_api_url = f'https://git.cs.dal.ca/api/v4/projects/{repo_id}/repository/contributors'
        headers = {'Authorization': f'{access_token}'}

        response = requests.get(gitlab_api_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Failed to fetch repository details from GitLab. Status code: {response.status_code}')

    @staticmethod
    def get_top_users_from_repo(repo_contributors, start_date, end_date):
        # Extract users and commit details from the GitLab repository contributors
        top_users = []

        for contributor in repo_contributors:
            # Assume 'commits' is the total number of commits
            commits_count = contributor.get('commits', 0)

            # Add user details to the top users list
            top_users.append({
                '_id': contributor['name'],  # You can use a unique identifier here
                'avatar_url': contributor.get('email', ''),  # Use 'email' or any other available field for avatar URL
                'commits': commits_count,
                'username': contributor['name']
            })

        return top_users


#-----------------------------------------------------------------------------------
class GitLabService:

    @staticmethod
    def fetch_commits_for_branch(repo_id, branch_name, start_date, end_date, access_token):
      
        commits_url = f'https://git.cs.dal.ca/api/v4/projects/{repo_id}/repository/commits'
      
        params = {
            'since': start_date,
            'until': end_date,
            'ref_name':branch_name,
            'per_page':100000
        }
        headers = {
            'Authorization': f'{access_token}',
        }

        response = requests.get(commits_url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Failed to fetch commits for repository {repo_id}. Status code: {response.status_code}')

    @staticmethod
    def extract_unique_contributors(commits_data):
        unique_contributors = set()
        
        for commit in commits_data:
            unique_contributors.add(commit['author_email'])
       
        return unique_contributors

    @staticmethod
    def get_active_contributors_count(repository_ids, start_date, end_date, access_token):
        
        unique_contributors = set()

        for repo_id in repository_ids:
            branches_data = GitLabService.fetch_repository_branches(repo_id, access_token)
            for branch in branches_data:
                branch_name = branch['name']
                commits_data = GitLabService.fetch_commits_for_branch(repo_id, branch_name, start_date, end_date, access_token)   
                unique_contributors.update(GitLabService.extract_unique_contributors(commits_data))

        # print(f'{unique_contributors}')
        return len(unique_contributors)
    
    @staticmethod
    def fetch_repository_branches(repo_id, access_token):
        branches_url = f'https://git.cs.dal.ca/api/v4/projects/{repo_id}/repository/branches'
        headers = {
            'Authorization': f'{access_token}',
        }

        response = requests.get(branches_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Failed to fetch repository branches. Status code: {response.status_code}')
                #-----------------------------------------------------------
    @staticmethod
    def get_total_contributors_count(repository_ids, access_token):
        total_contributors_emails = set()

        for repo_id in repository_ids:
            contributors_data = GitLabService.fetch_total_contributors(repo_id, access_token)
            contributors_emails = {contributor['email'] for contributor in contributors_data}
            total_contributors_emails.update(contributors_emails)

        total_all_repositories = len(total_contributors_emails)
        return total_all_repositories

    @staticmethod
    def fetch_total_contributors(repo_id, access_token):
        contributors_url = f'https://git.cs.dal.ca/api/v4/projects/{repo_id}/repository/contributors'
        headers = {
            'Authorization': f'{access_token}',
        }

        response = requests.get(contributors_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Failed to fetch total contributors for repository {repo_id}. Status code: {response.status_code}')