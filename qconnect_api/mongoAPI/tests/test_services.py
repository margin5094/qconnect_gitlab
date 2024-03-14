# from django.test import TestCase
# from mongoAPI.models.tokenModel import Token
# from mongoAPI.services.tokenService import save_token

# class TokenServiceTest(TestCase):
#     def setUp(self):
#         self.userId = 'test_user'
#         self.access_token = 'access123'
#         self.refresh_token = 'refresh123'

#     def test_save_token_creates_new_token(self):
#         """Test that save_token creates a new token entry."""
#         save_token(self.access_token, self.refresh_token, self.userId)
#         self.assertTrue(Token.objects.filter(id=self.userId).exists())

#     def test_save_token_updates_existing_token(self):
#         """Test that save_token updates an existing token."""
#         Token.objects.create(id=self.userId, access_token='old_access', refresh_token='old_refresh')
#         save_token('updated_access', 'updated_refresh', self.userId)
#         token = Token.objects.get(id=self.userId)
#         self.assertEqual(token.access_token, 'updated_access')
