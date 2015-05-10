"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.utils import override_settings
import django.core.mail
import re


class AccountsTest(TestCase):
    fixtures = ['users.json']

    def test_login(self):
        """
        Tests that test user can login and it redirects.
        """
        # First check for the default behavior
        response = self.client.get('/accounts/')
        self.assertRedirects(response, '/accounts/login/?next=/accounts/')
        response = self.client.post('/accounts/login/', data={'username': 'testuser', 'password': 'testuser'}, follow=True)

        self.assertRedirects(response, '/accounts/')

        # Check the user is logged in and there is a logout link
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Sign out')

    def test_homepage(self):
        response = self.client.get('/')
        self.assertContains(response, 'Sign in')
        self.client.login(username="testuser", password="testuser")
        response = self.client.get('/')
        self.assertContains(response, 'Sign out')

    def test_username_restrictions_enforced_too_short(self):
        """
        Test that the username requirements for registering are enforced
        """
        response = self.client.post('/accounts/register',
            data={'username': 't', 'password': 'testuser', 'email': 'qwerty@example.com'})

        self.assertContains(response, 'errorlist')
        self.assertContains(response, 'Ensure this value has at least 2 characters')

    def test_username_restrictions_enforced_too_long(self):
        """
        Test that the username requirements for registering are enforced
        """
        response = self.client.post('/accounts/register',
            data={'username': 'abcdefghi', 'password': 'testuser', 'email': 'qwerty@example.com'})

        self.assertContains(response, 'errorlist')
        self.assertContains(response, 'Ensure this value has at most 8 characters')

    def test_username_restrictions_enforced_non_letter(self):
        """
        Test that the username requirements for registering are enforced
        """
        response = self.client.post('/accounts/register',
            data={'username': 'abcd1234', 'password': 'testuser', 'email': 'qwerty@example.com'})

        self.assertContains(response, 'errorlist')
        self.assertContains(response, 'Enter a valid value')

    def test_email_restrictions_enforced(self):
        """
        Test that the username requirements for registering are enforced
        """
        response = self.client.post('/accounts/register',
            data={'username': 'abcd', 'password': 'testtest', 'email': 'qwertyrexample.com'})

        self.assertContains(response, 'errorlist')
        self.assertContains(response, 'Enter a valid email address')

    def test_password_restrictions_enforced(self):
        """
        Test that the username requirements for registering are enforced
        """
        response = self.client.post('/accounts/register',
            data={'username': 'abcd', 'password': 'test', 'email': 'qwerty@example.com'})

        self.assertContains(response, 'errorlist')
        self.assertContains(response, 'Ensure this value has at least 5 characters')

    def test_non_existent_user_cant_log_in(self):
        response = self.client.post('/accounts/login/',
            data={'username': 'abcd', 'password': 'testtest'})

        self.assertTrue(response.status_code == 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_non_existent_user_can_visit_log_out_page(self):
        response = self.client.post('/accounts/logout', follow=False)

        self.assertContains(response, 'You have been logged out')
        self.assertTrue(response.status_code == 200)

    def test_register_user(self):
        response = self.client.get('/accounts/register')
        self.assertTrue('form' in response.context)

        response = self.client.post('/accounts/register',
            data={'username': 'abcde', 'password': 'testtest', 'email': 'qwertyq@example.com'},
            follow=True)

        self.assertContains(response, '/accounts/login')
        self.assertContains(response, 'login')

        response = self.client.post('/accounts/login/',
            data={'username': 'abcde', 'password': 'testtest'},
            follow=True)

        self.assertTrue(response.status_code == 200)
        self.assertContains(response, 'abcde')
        self.assertContains(response, 'Sign out')

    def test_register_user_duplicate_username(self):
        response = self.client.post('/accounts/register',
            data={'username': 'abcde', 'password': 'testtest', 'email': 'qwerty@example.com'},
            follow=True)

        response = self.client.post('/accounts/register',
            data={'username': 'abcde', 'password': '12345678', 'email': '1qwerty@example.com'},
            follow=True)

        self.assertTrue(response.status_code == 200)
        self.assertContains(response, 'Username or email exists.')

    def test_register_user_duplicate_email(self):
        response = self.client.post('/accounts/register',
            data={'username': 'abcde', 'password': 'testtest',  'email': 'qwerty@example.com'},
            follow=True)

        response = self.client.post('/accounts/register',
            data={'username': 'abcdef', 'password': '12345678', 'email': 'qwerty@example.com'},
            follow=True)

        self.assertTrue(response.status_code == 200)
        self.assertContains(response, 'Username or email exists.')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_reset_password(self):
        # Set up the user
        response = self.client.post('/accounts/register',
            data={'username': 'abcd', 'password': 'testtest', 'email': 'qwerty@example.com'},
            follow=True)

        # Try and reset the password
        response = self.client.post('/accounts/password_reset/',
            data={'email': 'qwerty@example.com'},
            follow=True)

        self.assertContains(response, 'Password reset done')
        self.assertTrue(len(django.core.mail.outbox) == 1)
        self.assertTrue('Password reset on ' in django.core.mail.outbox[0].subject)
        self.assertTrue('Someone asked for password reset for email %s. Follow the link below:' % 'qwerty@example.com' in django.core.mail.outbox[0].body)

        # Grab the link
        match = re.search(r'http://[^/]+(.+)$', django.core.mail.outbox[0].body)
        self.assertTrue(len(match.groups()) == 1)
        link = match.groups()[0]

        # Get the link
        response = self.client.get(link)
        self.assertContains(response, 'New password')
        self.assertContains(response, 'New password confirmation')

        # Set a new password
        response = self.client.post('/accounts/password_reset/',
                data={'new_password1': '12345678', 'new_password2': '12345678', 'email': 'qwerty@example.com'},
            follow=True)

        self.assertContains(response, 'Password reset done')

    def test_public_profile(self):

        # Set up the user
        response = self.client.post('/accounts/register',
            data={'username': 'abcd', 'password': 'testtest', 'email': 'qwerty@example.com'},
            follow=True)

        self.client.login(username='testuser', password='testuser')
        response = self.client.get('/accounts/user/testuser')
        self.assertTrue('username' in response.context)

    def test_public_profile_anonymous(self):
        # Set up the user
        response = self.client.post('/accounts/register',
            data={'username': 'abcd', 'password': 'testtest', 'email': 'qwerty@example.com'},
            follow=True)

        response = self.client.get('/accounts/user/testuser', follow=True)

        self.assertFalse('username' in response.context)


    def test_public_profile_anonymous_404(self):
        # Set up the user
        response = self.client.post('/accounts/register',
            data={'username': 'abcd', 'password': 'testtest', 'email': 'qwerty@example.com'},
            follow=True)

        response = self.client.get('/accounts/user/nouser', follow=True)

        self.assertFalse(response.status_code == 404)
