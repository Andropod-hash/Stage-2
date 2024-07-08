from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from Org.models import Organization

User = get_user_model()

class OrganizationAccessTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            firstName='User1',
            lastName='Example',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            firstName='User2',
            lastName='Example',
            password='password2'
        )
        self.organization = Organization.objects.create(
            name="User1's Organization",
            created_by=self.user1
        )
        self.organization.members.add(self.user1)

    def test_user_cannot_access_other_users_organization(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('organization-detail', args=[self.organization.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
