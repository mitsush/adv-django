import jwt
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.verify_email_url = reverse('verify-email')
        
        # Test user data
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123',
            'role': 'job_seeker'
        }
        
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(
            self.register_url, self.user_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        # User should be inactive until email is verified
        self.assertEqual(User.objects.get().is_active, False)
        
    def test_user_cannot_login_before_verification(self):
        """Test that a user cannot login before email verification"""
        # Register user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Try to login
        login_data = {
            'username': 'testuser',
            'password': 'securepassword123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_email_verification(self):
        """Test email verification process"""
        # Register user
        self.client.post(self.register_url, self.user_data, format='json')
        user = User.objects.get(username='testuser')
        
        # Generate verification token manually for test
        payload = {
            'user_id': user.id,
            'type': 'email_verification'
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Verify email
        response = self.client.post(
            self.verify_email_url, 
            {'token': token}, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # User should now be able to login
        login_data = {
            'username': 'testuser',
            'password': 'securepassword123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        
    def test_registration_with_invalid_data(self):
        """Test registration with invalid data"""
        # Missing required fields
        invalid_data = {
            'username': 'testuser',
            'password': 'securepassword123'
        }
        response = self.client.post(
            self.register_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Password mismatch
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepassword123',
            'confirm_password': 'differentpassword',
            'role': 'job_seeker'
        }
        response = self.client.post(
            self.register_url, invalid_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Create and activate user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123',
            is_active=True
        )
        
        # Try to login with incorrect password
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
