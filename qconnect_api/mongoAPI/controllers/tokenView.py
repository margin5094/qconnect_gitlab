from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mongoAPI.services.tokenService import save_token

class TokenAPIView(APIView):

    def post(self, request):
        access_token = request.data.get('access_token')
        refresh_token = request.data.get('refresh_token')
        userId='f4613ff9-8160-48f9-af20-5dc03c051e7f'
        print(f"{access_token}")
        if access_token and refresh_token:
            save_token(access_token, refresh_token,userId)
            return Response({"status": "Token saved successfully"})
        return Response({"error": "Invalid request"}, status=400)
