from mongoAPI.models.tokenModel import Token

def save_token(access_token, refresh_token, userId):
    
    token, created = Token.objects.update_or_create(
        id=userId, 
        defaults={'access_token': access_token, 'refresh_token': refresh_token},
    )
    return token
