from __future__ import unicode_literals

import datetime, os
from django.test import TestCase
from articles.models import Article
from django.contrib.auth.models import User
from articles.views import _get_images_in_text
from django.urls import reverse


class ArticleImageTest(TestCase):

    def setUp(self):
        user = User.objects.create_user('testuser', email='testuser@example.com', password='testuser')
        user.first_name = 'John'
        user.last_name = 'Doe'
        user.save()

    def create_articles(self, number_of_articles=1, published=True):
        self.client.login(username="testuser", password="testuser")
        for i in range(1, number_of_articles + 1):
            response = self.client.post('/articles/new',
                {
                    'title': 'New article %d title' % i,
                    'body': 'New article %d body' % i,
                    'published' : published
                })
        self.client.logout()

    def test_anonymous_cant_see_form(self):
        # Check
        response = self.client.get('/articles/images/new', follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_create_image(self):
        # Setup
        self.create_articles(1)

        # Check form contains the fields we need
        self.client.login(username="testuser", password="testuser")
        response = self.client.get('/articles/images/new')

        self.assertContains(response, 'id_title')
        self.assertContains(response, 'id_article')
        self.assertContains(response, 'id_image')

        # Create an image
        response = self.client.post('/articles/images/new',
            {
                'title': 'New image title',
                'article': 1,
                'image': open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'rb'),
            },
            follow=True)

        self.assertContains(response, 'New image title')
        self.assertContains(response, 'ID')
        self.assertContains(response, response.context['image'].pk)
        self.assertTemplateUsed(response, 'articles/article_image.html')

    def test_update_image(self):
        # Setup
        self.create_articles(1)

        # Check form contains the fields we need
        self.client.login(username="testuser", password="testuser")

        # Create an image
        response = self.client.post('/articles/images/new',
            {
                'title': 'New image title',
                'article': 1,
                'image': open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'rb'),
            },
            follow=True)

        self.assertContains(response, 'New image title')
        pk = response.context['image'].pk

        response = self.client.get('/articles/images/%d/edit' % pk)
        self.assertContains(response, 'id_title')
        self.assertNotContains(response, 'id_image')

        response = self.client.post('/articles/images/%d/edit' % pk,
            {
                'title': 'Updated image title',
            },
            follow=True)

        self.assertTemplateUsed(response, 'articles/article_image.html')
        self.assertContains(response, 'Updated image title')

    def test_delete_image(self):
        # Setup
        self.create_articles(1)

        # Check form contains the fields we need
        self.client.login(username="testuser", password="testuser")

        # Create an image
        response = self.client.post('/articles/images/new',
            {
                'title': 'New image title',
                'article': 1,
                'image': open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'rb'),
            },
            follow=True)

        self.assertContains(response, 'New image title')
        pk = response.context['image'].pk
        self.assertTrue(str(response.context['image']) == 'New image title')

        # Try and delete
        response = self.client.get('/articles/images/%d/delete' % pk)
        self.assertTemplateUsed(response, 'articles/articleimage_confirm_delete.html')

        response = self.client.post('/articles/images/%d/delete' % pk, {}, follow=True)
        self.assertTemplateUsed(response, 'articles/article_image_list.html')

        response = self.client.get('/articles/images/%d' % pk)
        self.assertTrue(response.status_code == 404)


    def test_retrieve_image(self):
        # Setup
        self.create_articles(1)

        # Check form contains the fields we need
        self.client.login(username="testuser", password="testuser")

        # Create an image
        response = self.client.post('/articles/images/new',
            {
                'title': 'New image title',
                'article': 1,
                'image': open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'rb'),
            },
            follow=True)

        self.assertContains(response, 'New image title')
        pk = response.context['image'].pk

        response = self.client.get('/articles/images/%d' % pk)
        self.assertTemplateUsed(response, 'articles/article_image.html')
        self.assertContains(response, 'New image title')

    def test_image_anon(self):
        # Setup
        self.create_articles(1)

        # Check form contains the fields we need
        self.client.login(username="testuser", password="testuser")

        # Create an image
        response = self.client.post('/articles/images/new',
            {
                'title': 'New image title',
                'article': 1,
                'image': open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'rb'),
            },
            follow=True)

        self.assertContains(response, 'New image title')
        pk = response.context['image'].pk

        self.client.logout()

        response = self.client.get('/articles/images/%d' % pk)
        self.assertTemplateUsed(response, 'articles/article_image.html')
        self.assertContains(response, 'New image title')

        response = self.client.get('/articles/images/%d/edit' % pk)
        self.assertTrue(response.status_code == 302)
        self.assertTrue('login' in response.url)

        response = self.client.post('/articles/images/%d/edit' % pk)
        self.assertTrue(response.status_code == 302)
        self.assertTrue('login' in response.url)

        response = self.client.get('/articles/images/%d/delete' % pk)
        self.assertTrue(response.status_code == 302)
        self.assertTrue('login' in response.url)

        response = self.client.post('/articles/images/%d/delete' % pk)
        self.assertTrue(response.status_code == 302)
        self.assertTrue('login' in response.url)

        # Check the delete didn't delete
        response = self.client.get('/articles/images/%d' % pk)
        self.assertTemplateUsed(response, 'articles/article_image.html')
        self.assertContains(response, 'New image title')
