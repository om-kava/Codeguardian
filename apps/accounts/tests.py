from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('api_register')
        self.login_url = reverse('api_login')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'test@example.com'
        }

    def test_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_login(self):
        # Create user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Test login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
