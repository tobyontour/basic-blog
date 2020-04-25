"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

from django.test import TestCase
from django.test.utils import override_settings


class ConfigTest(TestCase):

    def test_google_webmaster_off(self):
        response = self.client.get('/')
        self.assertNotContains(response, '<meta name="google-site-verification"')
        self.assertTrue(response.context['GOOGLE_SITE_VERIFICATION'] is None)

    def test_google_webmaster_on(self):
        with self.settings(GOOGLE_SITE_VERIFICATION='this_is_a_test_string'):
            response = self.client.get('/')
            self.assertContains(response, '<meta name="google-site-verification" content="this_is_a_test_string">')
            self.assertTrue(response.context['GOOGLE_SITE_VERIFICATION'] == 'this_is_a_test_string', msg="'%s' != 'this_is_a_test_string'" % response.context['GOOGLE_SITE_VERIFICATION'])


class SearchTest(TestCase):
    def test_search(self):
        response = self.client.get('/search')
        self.assertContains(response, '<input type="search"')
