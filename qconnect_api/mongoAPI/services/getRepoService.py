import requests

def fetch_gitlab_projects(access_token):
    gitlab_api_url = 'https://git.cs.dal.ca/api/v4/projects'
    params = {'membership': 'true', 'per_page': 10000}
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(gitlab_api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        projects = response.json()
        # Filter the projects to return only id and name for each
        filtered_projects = [{'id': project['id'], 'name': project['name']} for project in projects]
        return filtered_projects
    else:
        raise Exception('Wrong token or token expired!')

