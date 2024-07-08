from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterEndpointTest(APITestCase):
    def test_register_user_successfully(self):
        data = {
            'email': 'testuser@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'password': 'testpassword123'
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['firstName'], 'Test')
        self.assertEqual(response.data['data']['user']['lastName'], 'User')
        self.assertEqual(response.data['data']['user']['email'], 'testuser@example.com')

    def test_login_user_successfully(self):
        # First, register the user
        self.client.post(reverse('register'), {
            'email': 'testuser@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'password': 'testpassword123'
        }, format='json')

        # Then, try to log in
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])

    def test_register_missing_fields(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        error_fields = [error['field'] for error in response.data['errors']]
        self.assertIn('firstName', error_fields)
        self.assertIn('lastName', error_fields)

    def test_register_duplicate_email(self):
        # First, register the user
        self.client.post(reverse('register'), {
            'email': 'testuser@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'password': 'testpassword123'
        }, format='json')

        # Try to register the same email again
        data = {
            'email': 'testuser@example.com',
            'firstName': 'Another',
            'lastName': 'User',
            'password': 'anotherpassword123'
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        error_fields = [error['field'] for error in response.data['errors']]
        self.assertIn('email', error_fields)
