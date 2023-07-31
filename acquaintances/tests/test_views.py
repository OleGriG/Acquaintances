from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from api.models import User, Like


class RegistrUserViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('registr-user-view')
        self.valid_payload = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.invalid_payload = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'invalidemail',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user_valid_payload(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)

    def test_create_user_invalid_payload(self):
        response = self.client.post(self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)


class UserListViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('user-list-view')
        self.user1 = User.objects.create(username='user1', email='user1@example.com', first_name='User', last_name='1')
        self.user2 = User.objects.create(username='user2', email='user2@example.com', first_name='User', last_name='2')

    def test_get_user_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_user_list_with_distance_filter(self):
        response = self.client.get(self.url, {'distance': '1000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_user_list_with_sex_filter(self):
        response = self.client.get(self.url, {'sex': 'M'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_user_list_with_name_filter(self):
        response = self.client.get(self.url, {'first_name': 'User'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_user_list(self):
        response = self.client.get(self.url, {'search': 'User 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class MatchViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

    def test_match_view_with_existing_users(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(reverse('match', args=[self.user2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Успешно оценено')
        self.assertTrue(Like.objects.filter(participant=self.user1, liked_participant=self.user2).exists())

    def test_match_view_with_non_existing_user(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(reverse('match', args=[999]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Участник не найден')

    def test_match_view_with_mutual_like(self):
        Like.objects.create(participant=self.user1, liked_participant=self.user2)
        self.client.login(username='user2', password='password2')
        response = self.client.post(reverse('match', args=[self.user1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Взаимная симпатия')
        self.assertTrue(Like.objects.filter(participant=self.user2, liked_participant=self.user1).exists())