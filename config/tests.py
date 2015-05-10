"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from articles.models import Article

class HomeTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('testuser', 'testuser@example.com', 'testuser')

    def create_articles(self, number_of_articles=1, published=True):

        self.client.login(username="testuser", password="testuser")
        for i in range(1, number_of_articles + 1):
            response = self.client.post('/articles/new',
                {
                    'title': 'New article %d title' % i,
                    'body': 'New article %d body' % i,
                    'published' : published
                }, follow=True)
            self.assertTrue(response.status_code == 200)
        self.client.logout()
        self.assertTrue(len(Article.objects.all()) == number_of_articles)

    def test_homepage(self):
        self.create_articles(20)
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

        self.assertTrue('articles' in response.context)
        self.assertTrue(len(response.context['articles']) == 10)

