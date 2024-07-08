from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from datetime import timedelta
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class TokenGenerationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            firstName='Test',
            lastName='User',
            password='testpassword123'
        )

    def test_token_generation(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        self.assertEqual(access_token.payload['user_id'], str(self.user.userId))