import datetime, os
from django.test import TestCase
from articles.models import Article
from django.contrib.auth.models import User
from articles.views import _get_images_in_text
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


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
        f = SimpleUploadedFile("file.txt", "file_content")
        response = self.client.post('/articles/images/new',
            {
                'title': 'New image title',
                'article': 1,
                'image': open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'r'),
            },
            follow=True)

        self.assertContains(response, 'New image title')
        self.assertContains(response, 'ID')
        self.assertContains(response, response.context['image'].pk)
        self.assertTemplateUsed(response, 'articles/article_image.html')
