from account.models import User
from rest_framework.test import APITestCase
from account.serializers import UserSerializer

class UserSerializerTestCase(APITestCase):
    def test_user_serializer_valid_data(self):
        data = {
            'email':'test@example.com',
            'name': 'Test User',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})

    def test_user_serializer_password_mismatch(self):
        data = {
            'email':'test@example.com',
            'name': 'Test User',
            'password': 'testpassword',
            'confirm_password': 'mismatchpassword'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['non_field_errors'][0], "Password and Confirm_Password doesn't match.")

    def test_user_serializer_duplicate_email(self):
        User.objects.create_user(email='existinguser@example.com', password='testpassword', name='Test User')

        data = {
            'email': 'existinguser@example.com',  # Duplicate email
            'name': 'Test User',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }

        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['email'][0], 'user with this Email already exists.')

    def test_user_serializer_create(self):
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.create(serializer.validated_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertFalse(user.is_active)

    def test_user_serializer_update(self):
        user = User.objects.create_user(email='existinguser@example.com', password='testpassword', name='Test User')

        data = {
            'name': 'Updated User'
        }

        serializer = UserSerializer(instance=user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.update(user, serializer.validated_data)
        self.assertEqual(updated_user.name, 'Updated User')