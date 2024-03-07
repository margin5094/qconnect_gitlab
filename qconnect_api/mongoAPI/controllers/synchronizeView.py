from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from mongoAPI.services.synchronizeService import get_refresh_token_by_id, get_new_accessToken
class RefreshTokenActionAPIView(APIView):
    def post(self, request):
        token_id = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'
        
        # Get refresh token by ID
        refresh_token = get_refresh_token_by_id(token_id)
        if refresh_token is None:
            return JsonResponse({"error": "Token not found"}, status=404)
        print(f'{refresh_token}')
        # Perform your custom logic with the refresh token
        result = get_new_accessToken(refresh_token,token_id)
        
        # Return a response based on your custom logic result
        return JsonResponse(result)
