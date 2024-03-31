import requests
from mongoAPI.models.MergeRequestModel import MergeRequest
from mongoAPI.models.CommitsModel import Commit
from mongoAPI.models.ProjectsModel import Project
from mongoAPI.models.PaginationInfo import PaginationInfo
from django.db import IntegrityError
from django.utils.dateparse import parse_datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from mongoAPI.Constants import GITLAB_API_URL


#----------------------fetch gitlab projects--------------------
def fetch_and_store_gitlab_projects(userId, access_token):
    gitlab_projects_url = f"{GITLAB_API_URL}projects"
    params = {'membership': 'true', 'per_page': 10000}
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(gitlab_projects_url, headers=headers, params=params)
        response.raise_for_status()
        projects = response.json()
        
        # Ensure keys are strings
        repo_data = {str(project['id']): project['name'] for project in projects}

        # Model's fields
        obj, created = Project.objects.update_or_create(
            userId=userId,
            defaults={'repos': repo_data}
        )
        
        # print(f'Object created: {created}, Object ID: {obj.pk}')
        return {"status": "success", "message": "Projects fetched and stored successfully.", "created": created}

    except requests.exceptions.RequestException as e:
        # print(f'Request error: {str(e)}')
        return {"status": "error", "message": str(e)}

    except Exception as e:
        # print(f'Unexpected error: {str(e)}')
        return {"status": "error", "message": "An unexpected error occurred."}


#------------------------------fetch_and_store_merge_requests----------------------------
def fetch_and_store_merge_requests(repositoryId, access_token):
    base_url = f"{GITLAB_API_URL}projects/{repositoryId}/merge_requests"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Attempting to fetch the repository info from the database
    repo_info, created = PaginationInfo.objects.update_or_create(repository_id=repositoryId)

    page = repo_info.merge_requests_last_page
    per_page = 100
    total_merge_requests_count = 0
    new_merge_requests = []

    while True:
        params = {'per_page': per_page, 'page': page}
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            merge_requests = response.json()
            if not merge_requests:  # Break if no more merge requests
                break
            
            existing_mr_ids = set(MergeRequest.objects.filter(repositoryId=repositoryId).values_list('merge_request_id', flat=True))
            for mr in merge_requests:
                if mr['id'] not in existing_mr_ids:
                    created_at = parse_datetime(mr['created_at'])
                    merged_at = parse_datetime(mr['merged_at']) if mr.get('merged_at') else None
                    new_merge_requests.append(MergeRequest(
                        repositoryId=repositoryId,
                        merge_request_id=mr['id'],
                        state=mr['state'],
                        created_at=created_at,
                        merged_at=merged_at
                    ))
            
            total_merge_requests_count += len(merge_requests)
            page += 1  # Incrementing to fetch the next page
        else:
            raise Exception("Failed to fetch merge requests from the API.")

    # Bulk insert new merge requests
    if new_merge_requests:
        MergeRequest.objects.bulk_create(new_merge_requests)
        # print(f'{page}')
        repo_info.merge_requests_last_page = page - 1  # Update to the last successfully fetched page
        repo_info.save()


#---------------------fetch all commits-------------------------------------------------------
    
def update_branches_info(repository_id, access_token):
    branches = get_gitlab_branches(repository_id, access_token)
    repo_info, _ = PaginationInfo.objects.get_or_create(repository_id=repository_id)
    
    # Initialize or update branches data
    updated_branches_info = []
    for branch in branches:
        branch_info = next((item for item in repo_info.branches if item['name'] == branch['name']), None)
        if branch_info is None:
            # Add new branch info if it doesn't exist
            updated_branches_info.append({'name': branch['name'], 'last_commit_page': 1})
        else:
            # Keep existing branch info including last commit page
            updated_branches_info.append(branch_info)
    
    # Update branches field in PaginationInfo
    repo_info.branches = updated_branches_info
    repo_info.save()

def get_gitlab_branches(repository_id, access_token):
    url = f"{GITLAB_API_URL}projects/{repository_id}/repository/branches"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, params={'per_page': 10000})
    if response.status_code == 200:
        return response.json()
    else:
        return []

def fetch_commits_for_branch(repository_id, branch_name, access_token, last_page):
    commits = []
    page = last_page
    while True:
        url = f"{GITLAB_API_URL}projects/{repository_id}/repository/commits"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {'ref_name': branch_name, 'per_page': 100, 'page': page}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200 and response.json():
            commits.extend(response.json())
            page += 1
        else:
            break
    return commits, page - 1  # Return the last page successfully fetched

def fetch_and_store_commits(repository_id, access_token):
    # Update branches information in PaginationInfo before fetching commits
    update_branches_info(repository_id, access_token)
    
    repo_info = PaginationInfo.objects.get(repository_id=repository_id)
    all_commits_dict = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_branch = {}
        for branch_info in repo_info.branches:
            last_page = branch_info['last_commit_page']
            future = executor.submit(fetch_commits_for_branch, repository_id, branch_info['name'], access_token, last_page)
            future_to_branch[future] = branch_info['name']
        
        for future in as_completed(future_to_branch):
            branch_name = future_to_branch[future]
            branch_commits, last_page = future.result()

            # Find the branch in repo_info.branches and update its last_commit_page
            for branch_info in repo_info.branches:
                if branch_info['name'] == branch_name:
                    branch_info['last_commit_page'] = last_page
                    break

            for commit in branch_commits:
                all_commits_dict[commit['id']] = commit

    repo_info.save()

    existing_commit_ids = set(Commit.objects.filter(repositoryId=repository_id).values_list('commitId', flat=True))
    commits_to_create = []

    for commit_id, commit in all_commits_dict.items():
        if commit_id not in existing_commit_ids:
            committed_date_parsed = parse_datetime(commit['committed_date'])
            commits_to_create.append(Commit(
                commitId=commit_id,
                repositoryId=repository_id,
                committer_name=commit['committer_name'],
                committer_email=commit['committer_email'],
                committed_date=committed_date_parsed
            ))

    if commits_to_create:
        try:
            Commit.objects.bulk_create(commits_to_create, ignore_conflicts=True)
            print(f"Stored {len(commits_to_create)} unique commits in the database for repository {repository_id}.")
        except IntegrityError as e:
            print(f"An error occurred while inserting commits. Some commits may not have been inserted. Error: {e}")


