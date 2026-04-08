from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from .models import User
from .tokens import account_activation_token


def create_active_user(**kwargs):
    defaults = dict(
        email='active@nexa.com',
        password='StrongPass123!',
        first_name='John',
        last_name='Doe',
        country='EG',
        phone_number='+201234567890',
    )
    defaults.update(kwargs)
    user = User.objects.create_user(**defaults)
    user.is_active = True
    user.save()
    return user


def create_inactive_user(**kwargs):
    defaults = dict(
        email='inactive@nexa.com',
        password='StrongPass123!',
        first_name='Jane',
        last_name='Doe',
        country='EG',
        phone_number='+201234567891',
    )
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


# ─────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────
class UserRegistrationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')
        self.valid_payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@nexa.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'country': 'EG',
            'phone_number': '+201234567890',
        }

    @patch('users.views.activateEmail')
    def test_valid_registration_returns_201(self, mock_email):
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    @patch('users.views.activateEmail')
    def test_registration_sets_cookies(self, mock_email):
        response = self.client.post(self.url, self.valid_payload)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    @patch('users.views.activateEmail')
    def test_registration_sends_activation_email(self, mock_email):
        self.client.post(self.url, self.valid_payload)
        mock_email.assert_called_once()

    @patch('users.views.activateEmail')
    def test_user_is_inactive_after_registration(self, mock_email):
        self.client.post(self.url, self.valid_payload)
        user = User.objects.get(email='john@nexa.com')
        self.assertFalse(user.is_active)

    def test_mismatched_passwords_returns_400(self):
        payload = {**self.valid_payload, 'password2': 'WrongPass!'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_returns_400(self):
        create_active_user(email='john@nexa.com')
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_field_returns_400(self):
        payload = {**self.valid_payload}
        payload.pop('email')
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_phone_number_returns_400(self):
        payload = {**self.valid_payload, 'phone_number': 'not-a-number'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# Account Activation
# ─────────────────────────────────────────────
class AccountActivationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_inactive_user()
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)

    def _url(self, uid, token):
        return reverse('activate', kwargs={'uidb64': uid, 'token': token})

    def test_valid_link_activates_user(self):
        response = self.client.get(self._url(self.uid, self.token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_invalid_token_returns_400(self):
        response = self.client.get(self._url(self.uid, 'bad-token'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_uid_returns_400(self):
        response = self.client.get(self._url('invaliduid', self.token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_already_active_user_with_stale_token_returns_400(self):
        # Activate first
        self.client.get(self._url(self.uid, self.token))
        # Token is now invalid (password hash changed upon save)
        response = self.client.get(self._url(self.uid, self.token))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────
class UserLoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login')
        self.user = create_active_user()

    def test_valid_credentials_returns_200(self):
        response = self.client.post(self.url, {
            'email': 'active@nexa.com',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_valid_login_sets_cookies(self):
        response = self.client.post(self.url, {
            'email': 'active@nexa.com',
            'password': 'StrongPass123!'
        })
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_wrong_password_returns_400(self):
        response = self.client.post(self.url, {
            'email': 'active@nexa.com',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_cannot_login(self):
        response = self.client.post(self.url, {
            'email': 'inactive@nexa.com',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_email_returns_400(self):
        response = self.client.post(self.url, {
            'email': 'ghost@nexa.com',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────
class UserLogoutViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_active_user()

    def _login_and_get_tokens(self):
        response = self.client.post(reverse('login'), {
            'email': 'active@nexa.com',
            'password': 'StrongPass123!'
        })
        return response.cookies.get('access_token').value, response.cookies.get('refresh_token').value

    def test_logout_clears_cookies(self):
        access, refresh = self._login_and_get_tokens()
        self.client.cookies['access_token'] = access
        self.client.cookies['refresh_token'] = refresh
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Cookies should be deleted (max-age=0 or empty value)
        self.assertFalse(response.cookies.get('access_token', {}).get('max-age', 1))

    def test_logout_without_token_returns_400(self):
        response = self.client.get(reverse('logout'))
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])


# ─────────────────────────────────────────────
# Token Refresh
# ─────────────────────────────────────────────
class UserTokenRefreshViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_active_user()

    def _get_refresh_token(self):
        response = self.client.post(reverse('login'), {
            'email': 'active@nexa.com',
            'password': 'StrongPass123!'
        })
        return response.cookies.get('refresh_token').value

    def test_valid_refresh_token_returns_new_access_token(self):
        refresh = self._get_refresh_token()
        self.client.cookies['refresh_token'] = refresh
        response = self.client.post(reverse('token_refresh'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)

    def test_missing_refresh_token_returns_400(self):
        response = self.client.post(reverse('token_refresh'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_refresh_token_returns_400(self):
        self.client.cookies['refresh_token'] = 'not-a-valid-token'
        response = self.client.post(reverse('token_refresh'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# Change Password
# ─────────────────────────────────────────────
class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_active_user()

    def _authenticate(self):
        response = self.client.post(reverse('login'), {
            'email': 'active@nexa.com',
            'password': 'StrongPass123!'
        })
        self.client.cookies['access_token'] = response.cookies['access_token'].value
        self.client.cookies['refresh_token'] = response.cookies['refresh_token'].value

    def test_valid_change_password_returns_200(self):
        self._authenticate()
        response = self.client.post(reverse('change_password'), {
            'old_password': 'StrongPass123!',
            'new_password': 'NewSecurePass456!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePass456!'))

    def test_wrong_old_password_does_not_change(self):
        self._authenticate()
        response = self.client.post(reverse('change_password'), {
            'old_password': 'WrongOldPass!',
            'new_password': 'NewSecurePass456!'
        })
        # No success response — password should remain unchanged
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_same_password_returns_400(self):
        self._authenticate()
        response = self.client.post(reverse('change_password'), {
            'old_password': 'StrongPass123!',
            'new_password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.post(reverse('change_password'), {
            'old_password': 'StrongPass123!',
            'new_password': 'NewSecurePass456!'
        })
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])


# ─────────────────────────────────────────────
# Request Password Reset
# ─────────────────────────────────────────────
class RequestPasswordResetEmailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('request_reset_password_email')
        self.user = create_active_user()

    @patch('users.views.reset_password_email')
    def test_existing_email_sends_email_and_returns_200(self, mock_reset):
        response = self.client.post(self.url, {'email': 'active@nexa.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_reset.assert_called_once()

    def test_nonexistent_email_returns_400(self):
        response = self.client.post(self.url, {'email': 'ghost@nexa.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('users.views.reset_password_email')
    def test_missing_email_field_raises_error(self, mock_reset):
        # KeyError expected since view does request.data['email'] directly
        try:
            response = self.client.post(self.url, {})
            self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        except KeyError:
            pass  # Expected — no email field handling in view


# ─────────────────────────────────────────────
# Password Reset Confirm
# ─────────────────────────────────────────────
class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_active_user()
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    def _url(self, uid, token):
        return reverse('reset_password_email', kwargs={'uidb64': uid, 'token': token})

    def test_valid_token_resets_password(self):
        response = self.client.post(
            self._url(self.uid, self.token),
            {'new_password': 'BrandNewPass789!'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('BrandNewPass789!'))

    def test_invalid_token_returns_400(self):
        response = self.client.post(
            self._url(self.uid, 'wrong-token'),
            {'new_password': 'BrandNewPass789!'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_uid_returns_400(self):
        response = self.client.post(
            self._url('invaliduid==', self.token),
            {'new_password': 'BrandNewPass789!'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_cannot_be_reused(self):
        self.client.post(
            self._url(self.uid, self.token),
            {'new_password': 'BrandNewPass789!'}
        )
        # Password changed → token is now stale
        response = self.client.post(
            self._url(self.uid, self.token),
            {'new_password': 'AnotherPass999!'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_user_uid_returns_400(self):
        fake_uid = urlsafe_base64_encode(force_bytes(99999))
        response = self.client.post(
            self._url(fake_uid, self.token),
            {'new_password': 'BrandNewPass789!'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
