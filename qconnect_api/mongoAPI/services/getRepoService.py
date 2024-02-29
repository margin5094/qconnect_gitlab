import requests

def fetch_gitlab_projects(access_token):
    gitlab_api_url = 'https://git.cs.dal.ca/api/v4/projects'
    params = {'membership': 'true','per_page':10000}
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(gitlab_api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json() 
    else:
        raise Exception('Wrong token or token expired!')
