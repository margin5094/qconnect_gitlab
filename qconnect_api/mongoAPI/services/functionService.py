import requests
from mongoAPI.models.MergeRequestModel import MergeRequest

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
