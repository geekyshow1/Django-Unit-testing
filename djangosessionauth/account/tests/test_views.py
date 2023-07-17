from rest_framework.test import APITestCase, APIClient
from account.models import User
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework import status
import pdb

class RegsiterViewTestCase(APITestCase):
    def setUp(self):
        self.csrf_token = self._get_csrf_token()
        self.csrf_client = APIClient(enforce_csrf_checks=True)
    
    def _get_csrf_token(self):
      response = self.client.get(reverse('csrf_cookie'))  # Send a GET request to the csrf_cookie endpoint
      return response.cookies['csrftoken'].value
    
    def test_get_csrf_token(self):
        response = self.client.get(reverse('csrf_cookie'))
        self.assertTrue(response.cookies['csrftoken'].value)
        
    def test_register_view_success(self):
        url = reverse('register')

        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }
        headers = {'X-CSRFToken': self.csrf_token, 'Cookie':'csrftoken='+self.csrf_token}  # Include CSRF token in request headers
        response = self.csrf_client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['name'], 'Test User')

    def test_register_view_invalid_email(self):
        url = reverse('register')

        data = {
            'email': 'invalid_email',  # Invalid email format
            'name': 'Test User',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }

        headers = {'X-CSRFToken': self.csrf_token, 'Cookie':'csrftoken='+self.csrf_token}  # Include CSRF token in request headers

        response = self.csrf_client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Add additional assertions as needed

    def test_register_view_duplicate_email(self):
        User.objects.create_user(email='test@example.com', password='testpassword', name="Test User")

        url = reverse('register') 

        data = {
            'email': 'test@example.com',  # Duplicate email
            'name': 'Test User',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }

        headers = {'X-CSRFToken': self.csrf_token, 'Cookie':'csrftoken='+self.csrf_token}  # Include CSRF token in request headers

        response = self.csrf_client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ActivationConfirmTestCase(APITestCase):
    def test_activation_confirm_success(self):
        # Create a user with a valid activation link
        user = User.objects.create(email='test@example.com', is_active=False)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        url = reverse('activation_confirm')

        data = {
            'uid': uid,
            'token': token
        }

        # Send activation request
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Account activated successfully.')
        # Add additional assertions as needed


    def test_activation_confirm_already_activated(self):
        # Create a user with an already activated account
        user = User.objects.create(email='test@example.com', is_active=True)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        url = reverse('activation_confirm')

        data = {
            'uid': uid,
            'token': token
        }

        # Send activation request
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Account is already activated.')
        # Add additional assertions as needed

    def test_activation_confirm_missing_uid_token(self):
        url = reverse('activation_confirm')  

        data = {}  # Missing uid and token

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Missing uid or token.')
        # Add additional assertions as needed

    def test_activation_confirm_invalid_activation_link(self):
        url = reverse('activation_confirm')  

        data = {
            'uid': 'Ma',
            'token': 'dfgdfg4534sdffghf64565sdf'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid activation link.')
        # Add additional assertions as needed

class LoginViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', name='Test User')
        self.user.is_active = True
        self.user.save()

    def test_login_view_success(self):
        url = reverse('login')  

        data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }

        response = self.client.post(url, data, format='json')
        # pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Logged in successfully.')
        # Add additional assertions as needed

    def test_login_view_invalid_credentials(self):
        url = reverse('login')  

        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'  # Incorrect password
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Email or Password is incorrect.')
        # Add additional assertions as needed


class UserDetailViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', name='Test User')
        self.client.force_authenticate(user=self.user)

    def test_get_user_detail(self):
        url = reverse('user_detail') 

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['name'], 'Test User')
        self.assertEqual(response.data['is_staff'], False)  # Assuming is_staff is False for a regular user
        # Add additional assertions as needed

    def test_update_user_detail(self):
        url = reverse('user_detail')  

        data = {
            'name': 'New User'
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New User')
        # Add additional assertions as needed


class ChangePasswordViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', name='Test User')
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        url = reverse('change_password')  

        data = {
            'old_password': 'testpassword',
            'new_password': 'newpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password changed successfully.')
        # Add additional assertions as needed

    def test_change_password_invalid_old_password(self):
        url = reverse('change_password')  

        data = {
            'old_password': 'wrongpassword',  # Incorrect old password
            'new_password': 'newpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid old password.')
        # Add additional assertions as needed

class DeleteAccountViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', name='Test User')
        self.client.force_authenticate(user=self.user)

    def test_delete_account_success(self):
        url = reverse('user_delete')  

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['detail'], 'Account deleted successfully.')
        # Add additional assertions as needed

    def test_delete_account_unauthenticated(self):
        self.client.logout()

        url = reverse('user_delete')  

        response = self.client.delete(url)
     
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Add additional assertions as needed

class LogoutViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', name='Test User')
        self.client.force_authenticate(user=self.user)

    def test_logout_success(self):
        url = reverse('logout')  # Replace 'logout' with your actual URL name

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Logged out successfully.')
        # Add additional assertions as needed

    def test_logout_unauthenticated(self):
        self.client.logout()

        url = reverse('logout')  # Replace 'logout' with your actual URL name

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Add additional assertions as needed

class ResetPasswordEmailViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', name='Test User')

    def test_reset_password_email_success(self):
        url = reverse('reset_password_email')  

        data = {
            'email': 'test@example.com'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password reset email sent successfully.')
        # Add additional assertions as needed

    def test_reset_password_email_invalid_email(self):
        url = reverse('reset_password_email')  

        data = {
            'email': 'invalid@example.com'  # Invalid email
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'User with this email does not exist.')
        # Add additional assertions as needed

class ResetPasswordConfirmViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', name='Test User')

    def test_reset_password_confirm_success(self):
        url = reverse('reset_password_confirm') 

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        data = {
            'uid': uid,
            'token': token,
            'new_password': 'newpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password reset successful.')
        # Add additional assertions as needed

    def test_reset_password_confirm_invalid_link(self):
        url = reverse('reset_password_confirm') 

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        data = {
            'uid': uid,
            'token': token+'we',
            'new_password': 'newpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid reset password link.')
        # Add additional assertions as needed

    def test_reset_password_confirm_missing_fields(self):
        url = reverse('reset_password_confirm') 

        data = {
            'uid': 'validuid',
            'new_password': 'newpassword'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Missing uid or token.')
        # Add additional assertions as needed

    