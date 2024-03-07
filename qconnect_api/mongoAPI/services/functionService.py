import requests
from mongoAPI.models.MergeRequestModel import MergeRequest
from mongoAPI.models.CommitsModel import Commit
from mongoAPI.models.RepositoryModel import Repository
from mongoAPI.models.ContributorsModel import RepositoryContributors
from django.db import IntegrityError
from django.utils.dateparse import parse_datetime
from datetime import datetime

def fetch_and_store_merge_requests(repositoryId, access_token):
    url = f"https://git.cs.dal.ca/api/v4/projects/{repositoryId}/merge_requests"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'per_page': 100}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        merge_requests = response.json()
        
        for mr in merge_requests:
            # Parse 'created_at' directly
            created_at = parse_datetime(mr['created_at'])
            
            # Check if 'merged_at' is present and parse it; otherwise, use None
            merged_at = parse_datetime(mr['merged_at']) if mr.get('merged_at') else None
            
            # Use the parsed datetime objects directly without converting them back to string
            obj, created = MergeRequest.objects.get_or_create(
                repositoryId=repositoryId,
                merge_request_id=mr['id'],
                defaults={'state': mr['state'], 'created_at': created_at, 'merged_at': merged_at}
            )
    else:
        raise Exception("Failed to fetch merge requests from the API.")
#---------------------fetch all commits-------------------------------------------------------
def get_gitlab_branches(repository_id, access_token):
    url = f"https://git.cs.dal.ca/api/v4/projects/{repository_id}/repository/branches"
    params = {
        'per_page': 100000
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers,params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def get_gitlab_commits(repository_id, branch_name, access_token):
    url = f"https://git.cs.dal.ca/api/v4/projects/{repository_id}/repository/commits?ref_name={branch_name}"
    params = {
        'per_page': 100000
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers,params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def fetch_and_store_commits(repository_id, access_token):
    branches = get_gitlab_branches(repository_id, access_token)
    all_commits_dict = {}

    for branch in branches:
        branch_commits = get_gitlab_commits(repository_id, branch['name'], access_token)
        for commit in branch_commits:
            # Use commit ID as the key to ensure uniqueness
            all_commits_dict[commit['id']] = commit

    all_commits = list(all_commits_dict.values())
    existing_combinations = set(Commit.objects.filter(repositoryId=repository_id).values_list('commitId', flat=True))

    commits_to_create = []
    for commit in all_commits:
        if commit['id'] not in existing_combinations:
            # Parse the committed_date
            committed_date_parsed = datetime.strptime(commit['committed_date'], "%Y-%m-%dT%H:%M:%S.%f%z")
            commits_to_create.append(Commit(
                commitId=commit['id'], 
                repositoryId=repository_id, 
                committer_name=commit['committer_name'],
                committer_email=commit['committer_email'],
                committed_date=committed_date_parsed
            ))
    
    try:
        Commit.objects.bulk_create(commits_to_create, ignore_conflicts=True)
        print(f"Stored {len(commits_to_create)} unique commits in the database for repository {repository_id}.")
    except IntegrityError as e:
        print("An error occurred while inserting commits. Some commits may not have been inserted.")
        raise e
#--------------------------Total Contirbutors-----------------------
    
def fetch_and_store_contributors(repository_id, access_token):
    url = f"https://git.cs.dal.ca/api/v4/projects/{repository_id}/repository/contributors"
    params = {
        'per_page': 100000
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers,params=params)
    if response.status_code == 200:
        contributors = response.json()
        total_contributors = len(contributors)
        
        # Update or create the entry in MongoDB
        RepositoryContributors.objects.update_or_create(
            repositoryId=repository_id,
            defaults={'totalContributors': total_contributors},
        )
        print(f"Repository {repository_id} has {total_contributors} unique contributors.")
    else:
        print("Failed to fetch contributors.")

#----------------------------get repo id from object id----------------------------
# def resolve_repository_ids(objectIds):
#     try:
#         repositories = Repository.objects.filter(_id__in=objectIds).values_list('_id', flat=True)
#         return list(repositories)
#     except Repository.DoesNotExist:
#         return None