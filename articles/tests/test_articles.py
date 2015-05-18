"""
Tests for Articles
"""
import datetime
from django.test import TestCase
from articles.models import Article
from django.contrib.auth.models import User
from articles.views import _get_images_in_text

class ArticleTest(TestCase):

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

    def test_create_article(self):
        self.client.login(username="testuser", password="testuser")
        response = self.client.get('/articles/new')
        self.assertContains(response, 'Title')
        self.assertContains(response, 'Body')
        self.assertContains(response, 'Slug')

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
            },
            follow=True)

        self.assertNotContains(response, 'errorlist',
                msg_prefix='New article form did not submit')
        self.assertContains(response, 'New article')
        self.assertContains(response, 'New article body')
        self.assertTrue('article' in response.context)
        self.assertTrue(response.context['article'].published == False)
        self.assertTrue(str(response.context['article']) == 'New article')

        response = self.client.get('/articles/new-article')
        self.assertContains(response, 'New article')
        self.assertContains(response, 'New article body')

    def test_create_article_own_slug(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
                'slug': 'made-up-slug',
            },
            follow=True)

        self.assertContains(response, 'New article')
        self.assertTrue('article' in response.context)
        self.assertTrue(response.context['article'].slug == 'made-up-slug')

        response = self.client.get('/articles/new-article')
        self.assertTrue(response.status_code == 404)

        response = self.client.get('/articles/made-up-slug')
        self.assertContains(response, 'New article')
        self.assertNotContains(response, 'id_title')


    def test_create_article_not_logged_in(self):
        response = self.client.get('/articles/new', follow=True)
        self.assertContains(response, 'id_username')
        self.assertContains(response, 'id_password')

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
            },
            follow=True)
        self.assertContains(response, 'id_username')
        self.assertContains(response, 'id_password')

    def test_create_article_no_title(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': '',
                'body': 'New article body',
            },
            follow=True)
        self.assertContains(response, 'errorlist')
        self.assertContains(response, 'This field is required')

    def test_update_article(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article title',
                'body': 'New article body',
            },
            follow=True)

        response = self.client.get('/articles/new-article-title/edit')
        self.assertContains(response, 'id_title')
        self.assertContains(response, 'id_body')
        self.assertContains(response, 'id_published')
        self.assertContains(response, 'id_slug')
        self.assertContains(response, 'New article title')
        self.assertContains(response, 'New article body')

        response = self.client.post('/articles/new-article-title/edit',
            {
                'title': 'Updated title',
                'body': 'New article body updated',
                'slug': 'new-article-title',
                'published': True,
            },
            follow=True)

        self.assertTemplateUsed(response, 'articles/article.html')
        self.assertContains(response, 'Updated title')
        self.assertContains(response, 'New article body updated')

        response = self.client.get('/articles/new-article-title')
        self.assertContains(response, 'Updated title')
        self.assertContains(response, 'New article body updated')


    def test_update_article_not_logged_in(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
            },
            follow=True)

        self.client.logout()
        response = self.client.get('/articles/new-article/edit', follow=True)
        self.assertContains(response, 'id_username')
        self.assertContains(response, 'id_password')
        self.assertNotContains(response, 'id_title')

        response = self.client.post('/articles/new',
            {
                'title': 'Updated title',
                'body': 'New article body',
            },
            follow=True)
        self.assertContains(response, 'id_username')
        self.assertContains(response, 'id_password')

    def test_delete_article(self):
        self.create_articles(self, number_of_articles=3, published=True)
        # 'title': 'New article %d title' % i,
        # 'body': 'New article %d body' % i,
        # 'published' : published
        self.client.login(username="testuser", password="testuser")

        response = self.client.get('/articles/new-article-2-title')
        self.assertTrue(response.status_code == 200)

        response = self.client.get('/articles/new-article-2-title/delete')
        self.assertContains(response, 'Are you sure you want to delete New article 2 title')
        self.assertContains(response, 'Delete')

        # Delete article
        response = self.client.post('/articles/delete',
            {
            },
            follow=True)
 
        response = self.client.get('/articles/new-article-2-title')
        self.assertTrue(response.status_code == 404)
        response = self.client.get('/articles/new-article-1-title')
        self.assertTrue(response.status_code == 200)
        response = self.client.get('/articles/new-article-3-title')
        self.assertTrue(response.status_code == 200)

    def test_update_non_existent_article(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.get('/articles/new-article/edit', follow=True)
        self.assertTrue(response.status_code == 404)

    def test_retrieve_own_article_unpublished_article(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article title',
                'body': 'New article body',
            },
            follow=True)

        response = self.client.get('/articles/new-article-title')
        self.assertContains(response, 'New article title')
        self.assertContains(response, 'New article body')

    def test_retrieve_unpublished_article_not_logged_in(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article title',
                'body': 'New article body',
            },
            follow=True)

        self.client.logout()

        response = self.client.get('/articles/new-article-title')
        self.assertNotContains(response, 'New article title', status_code=404)

    def test_retrieve_published_article_not_logged_in(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article title',
                'body': 'New article body',
                'published' : True
            },
            follow=True)
        self.client.logout()
        response = self.client.get('/articles/new-article-title')
        self.assertContains(response, 'New article title')

    def test_retrieve_list(self):
        number_of_articles = 5
        self.create_articles(number_of_articles)
        response = self.client.get('/articles/')

        self.assertTrue(len(response.context['articles']) == number_of_articles)

    def test_article_body_uses_markdown(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': '''
Header
======
Header 2
--------
                '''
            },
            follow=True)

        self.assertContains(response, '<h1>Header</h1>',
                msg_prefix='Header 1 is not created by Markdown')
        self.assertContains(response, '<h2>Header 2</h2>',
                msg_prefix='Header 2 is not created by Markdown')

    def test_delete_article(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
            },
            follow=True)
        response = self.client.get('/articles/new-article/edit')
        self.assertContains(response, 'id_title')
        self.assertContains(response, 'id_body')
        self.assertContains(response, 'id_published')
        self.assertContains(response, 'id_slug')

        response = self.client.post('/articles/new',
            {
                'title': 'Updated title',
                'body': 'New article body',
            },
            follow=True)
        self.assertContains(response, 'Updated title')
        self.assertContains(response, 'New article body')

    def test_create_page(self):
        self.client.login(username="testuser", password="testuser")
        response = self.client.get('/articles/new')
        self.assertContains(response, 'Title')
        self.assertContains(response, 'Body')
        self.assertContains(response, 'Slug')

        response = self.client.post('/articles/new',
            {
                'title': 'New page',
                'body': 'New page body',
                'published': True,
                'is_page': True,
            },
            follow=True)

        self.assertContains(response, 'New page')
        self.assertContains(response, 'New page body')
        self.assertTrue('page' in response.context)
        self.assertTrue(response.context['page'].published == True)
        self.assertTrue(str(response.context['page']) == 'New page')

        response = self.client.get('/articles/new-page')
        self.assertTrue(response.status_code == 404)
        response = self.client.get('/new-page')
        self.assertContains(response, 'New page')
        self.assertContains(response, 'New page body')

    def test_home_page(self):
        self.create_articles(number_of_articles=10)
        response = self.client.get('/')

class ArticleParsingTest(TestCase):

    def test_text_parsing_for_images_1(self):
        self.assertEquals(_get_images_in_text(''), [])

    def test_text_parsing_for_images_2(self):
        self.assertEquals(_get_images_in_text('{image:72}'), [72])

    def test_text_parsing_for_images_3(self):
        self.assertEquals(_get_images_in_text(' {image:89}'), [89])

    def test_text_parsing_for_images_4(self):
        self.assertEquals(_get_images_in_text('''
Blah blah
{image:12}
  {image:23}{image:45}'''), [12,23,45])
