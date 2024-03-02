import requests
from mongoAPI.models.MergeRequestModel import MergeRequest
from mongoAPI.models.CommitsModel import Commit
from mongoAPI.models.ContributorsModel import RepositoryContributors
from django.db import IntegrityError

def fetch_and_store_merge_requests(repositoryId, access_token):
    url = f"https://git.cs.dal.ca/api/v4/projects/{repositoryId}/merge_requests"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'per_page': 100000
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        merge_requests = response.json()
        
        # Fetch existing merge request IDs for the repositoryId
        existing_mr_ids = set(MergeRequest.objects.filter(repositoryId=repositoryId)
                                              .values_list('merge_request_id', flat=True))
        
        # Prepare data for bulk insertion
        merge_requests_to_create = []
        for mr in merge_requests:
            # Check if the merge request already exists
            if mr['id'] not in existing_mr_ids:
                merge_requests_to_create.append(MergeRequest(
                    repositoryId=repositoryId,
                    merge_request_id=mr['id'],
                    data=mr  # Store the entire merge request data as is
                ))
        
        # Bulk create merge requests
        MergeRequest.objects.bulk_create(merge_requests_to_create)
        
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
    
    # Convert the dictionary back to a list for further processing or storing
    all_commits = list(all_commits_dict.values())
    
    # Fetch existing commit IDs to avoid duplication
    existing_commit_ids = set(Commit.objects.all().values_list('commitId', flat=True))
    
    # Prepare data for bulk insertion, excluding commits that already exist
    commits_to_create = []
    for commit in all_commits:
        if commit['id'] not in existing_commit_ids:
            commits_to_create.append(Commit(commitId=commit['id'], data=commit))
    
    # Bulk create commits, handling any exceptions if they occur
    try:
        Commit.objects.bulk_create(commits_to_create)
        print(f"Stored {len(commits_to_create)} unique commits in the database.")
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