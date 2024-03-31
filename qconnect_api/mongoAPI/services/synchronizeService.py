from mongoAPI.models.tokenModel import Token
import requests
from mongoAPI.services.tokenService import save_token
from mongoAPI.Constants import GITLAB_AUTH_URL
import os

def get_refresh_token_by_id(token_id):
    try:
        token = Token.objects.get(id=token_id)
        return token.refresh_token
    except Token.DoesNotExist:
        return None

def get_new_accessToken(refresh_token,token_id):
    # GitLab Application Credentials
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    redirect_uri = os.getenv('REDIRECT_URI ')
    
    # GitLab Token Endpoint for refreshing tokens
    token_url = GITLAB_AUTH_URL
    
    # Data to be sent in the POST request
    post_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
    }
    
    try:
        # Sending POST request to GitLab's token endpoint
        response = requests.post(token_url, data=post_data)
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        # Extracting new access and refresh token from the response
        new_tokens = response.json()
        new_access_token = new_tokens.get('access_token')
        new_refresh_token = new_tokens.get('refresh_token')
        if new_access_token and new_refresh_token:
            save_token(new_access_token, new_refresh_token,userId=token_id)
        return {
            "status": "Success",
            "message": "New access and refresh tokens generated",
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }
    except requests.RequestException as e:
        # Handling request errors
        return {
            "status": "Error",
            "message": f"Failed to refresh token: {str(e)}"
        }