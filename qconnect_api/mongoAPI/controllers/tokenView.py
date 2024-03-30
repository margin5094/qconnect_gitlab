from rest_framework.views import APIView
from rest_framework.response import Response
from mongoAPI.services.tokenService import save_token
from mongoAPI.services.functionService import fetch_and_store_gitlab_projects
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class TokenAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['access_token', 'refresh_token'],
            properties={
                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: "Token saved successfully",
            400: "Bad Request"
        }
    )
    def post(self, request):
        access_token = request.data.get('access_token')
        refresh_token = request.data.get('refresh_token')
        userId = 'f4613ff9-8160-48f9-af20-5dc03c051e7f'

        if access_token and refresh_token:
            save_token(access_token, refresh_token, userId)
            project_response = fetch_and_store_gitlab_projects(userId, access_token)

            if project_response['status'] == "success":
                return Response({"status": "Token saved successfully"})
            else:
                return Response({"error": project_response["message"]}, status=400)

        return Response({"error": "Invalid request"}, status=400)