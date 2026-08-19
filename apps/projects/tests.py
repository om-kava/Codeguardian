from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Project

class ProjectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.project_url = '/api/projects/'

    def test_create_project(self):
        data = {'name': 'Test API Project', 'description': 'Testing creation'}
        response = self.client.post(self.project_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, 'Test API Project')

    def test_retrieve_projects(self):
        Project.objects.create(owner=self.user, name='Project 1')
        response = self.client.get(self.project_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.project_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
