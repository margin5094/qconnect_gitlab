# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from mongoAPI.models.tokenModel import Token

# class TokenAPIViewTest(APITestCase):
#     def test_post_valid_tokens(self):
#         """Test the API view with valid tokens."""
#         url = reverse('token_api')
#         data = {'access_token': 'access123', 'refresh_token': 'refresh123'}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(Token.objects.count(), 1)

#     def test_post_invalid_request(self):
#         """Test the API view with invalid request data."""
#         url = reverse('token_api')
#         data = {}  # Empty data
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
