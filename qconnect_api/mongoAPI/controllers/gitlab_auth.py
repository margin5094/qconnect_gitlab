from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mongoAPI.Constants import SAVE_TOKEN
import requests
import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class GitLabAuth(APIView):
    @swagger_auto_schema(
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['code'],
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(description="Token retrieved successfully", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: "Code not provided",
            500: "Internal Server Error"
        }
    )
    def post(self, request):
        code = request.data.get('code')
        if code:
            try:
                response = requests.post(
                    "https://git.cs.dal.ca/oauth/token",
                    data={
                        'client_id':  os.getenv('CLIENT_ID'),
                        'client_secret': os.getenv('CLIENT_SECRET'),
                        'code': code,
                        'grant_type': 'authorization_code',
                        'redirect_uri': os.getenv('REDIRECT_URI'), 
                    }
                )
                data = response.json()
                
                # Call the API to obtain the token
                # Assuming you have configured your Django routes properly
                token_response = requests.post(
                    SAVE_TOKEN,
                    data={
                        'access_token': data['access_token'],
                        'refresh_token': data['refresh_token']
                    }
                )

                # Check if token retrieval was successful
                if token_response.status_code == 200:
                    return Response({'message': 'Token retrieved successfully'})
                else:
                    return Response({'error': 'Token retrieval failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Code not provided'}, status=status.HTTP_400_BAD_REQUEST)
