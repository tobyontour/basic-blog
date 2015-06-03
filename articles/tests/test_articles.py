"""
Tests for Articles
"""
import datetime, os
from django.test import TestCase
from articles.models import Article, ArticleTag
from django.contrib.auth.models import User
from articles.views import _get_images_in_text
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse


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

    def test_create_article_with_images(self):
        # Setup
        self.client.login(username="testuser", password="testuser")
        response = self.client.post('/articles/new',
                {
                    'title': 'New article title',
                    'body': 'With {image:1} and {image:2} so there.',
                    'published' : True,
                })

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
        img1 = response.context['image']

        f = SimpleUploadedFile("file.txt", "file_content")
        response = self.client.post('/articles/images/new',
            {
                'title': 'New second image title',
                'article': 1,
                'image': open(os.path.join(os.path.dirname(__file__), 'test_image.jpg'), 'r'),
            },
            follow=True)

        self.assertContains(response, 'New second image title')
        img2 = response.context['image']

        response = self.client.get('/articles/new-article-title')
        self.assertTrue(img1.image.url in response.context['body'])
        self.assertTrue(img2.image.url in response.context['body'])

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

    def test_create_article_with_tags(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
                'tags_text': 'tag 1, tag 2 ,tag3',
            },
            follow=True)

        self.assertContains(response, 'New article')

        self.assertTrue('article' in response.context)
        self.assertTrue(len(response.context['article'].tags.all()) == 3)

        tags = [x.title for x in response.context['article'].tags.all()]
        self.assertTrue('tag 1' in tags)
        self.assertTrue('tag 2' in tags)
        self.assertTrue('tag3' in tags)

        response = self.client.get('/articles/new-article')

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
        self.create_articles(number_of_articles=3, published=True)
        # 'title': 'New article %d title' % i,
        # 'body': 'New article %d body' % i,
        # 'published' : published
        self.client.login(username="testuser", password="testuser")

        response = self.client.get('/articles/new-article-2-title')
        self.assertTemplateUsed(response, 'articles/article.html')
        self.assertTrue(response.status_code == 200)

        response = self.client.get('/articles/new-article-2-title/delete')
        self.assertTemplateUsed(response, 'articles/article_confirm_delete.html')
        self.assertContains(response, 'Are you sure you want to delete "New article 2 title"?')
        self.assertContains(response, 'Delete')
        self.assertTrue('header_image' in response.context)

        # Delete article
        response = self.client.post('/articles/new-article-2-title/delete',
            {
            },
            follow=True)
 
        response = self.client.get('/articles/new-article-2-title')
        
        self.assertTrue(response.status_code == 404, msg="Expectec 404, got %d" % response.status_code)
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

    def test_article_list_page_article(self):
        self.create_articles(number_of_articles=10)
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'This is the article list page',
                'body': 'The quick brown fox',
                'published': True,
                'is_page': True,
                'slug': 'articles',
            },
            follow=True)

        response = self.client.get('/articles/')
        self.assertTrue(response.context['page'].title == 'This is the article list page')
        self.assertTrue(response.context['page'].body == 'The quick brown fox')

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

    def test_article_markdown_embeded_html(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': '''
Header
======
<em><strong><img src="#"></strong></em>
--------
                '''
            },
            follow=True)

        self.assertContains(response, '<h1>Header</h1>',
                msg_prefix='Header 1 is not created by Markdown')
        self.assertContains(response, '<em><strong><img src="#"></strong></em>',
                msg_prefix='Raw HTML not passed through Markdown')

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

    def test_page_list(self):
        self.client.login(username="testuser", password="testuser")
        response = self.client.post('/articles/new',
            {
                'title': 'Page one',
                'body': 'New page body 1',
                'published': True,
                'is_page': True,
            },
            follow=True)
        response = self.client.post('/articles/new',
            {
                'title': 'Page two',
                'body': 'New page body 1',
                'published': True,
                'is_page': True,
            },
            follow=True)

        response = self.client.get('/pages/')

        self.assertTrue(len(response.context['articles']) == 2)
        self.assertTemplateUsed('articles/article_list.html')


    def test_home_page(self):
        self.create_articles(number_of_articles=10)
        response = self.client.get('/')
        
    def test_home_page_article(self):
        self.create_articles(number_of_articles=10)
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'Home page article',
                'body': 'New home page body',
                'published': True,
                'is_page': True,
                'slug': 'home',
            },
            follow=True)

        response = self.client.get('/')
        self.assertTrue(response.context['home_article'].title == 'Home page article')
        self.assertTrue(response.context['home_article'].body == 'New home page body')

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


class ArticleTagsTest(TestCase):

    def setUp(self):
        user = User.objects.create_user('testuser', email='testuser@example.com', password='testuser')
        user.first_name = 'John'
        user.last_name = 'Doe'
        user.save()

    def test_tag_string(self):
        tag = ArticleTag(title="This is a title")
        self.assertTrue(str(tag) == "This is a title")

    def test_create_article_with_tags(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
                'tags_text': 'tag 1, tag 2 ,tag3',
            },
            follow=True)

        self.assertTemplateUsed(response, 'articles/article.html')
        self.assertContains(response, 'New article')

        self.assertTrue('article' in response.context)
        self.assertTrue(len(response.context['article'].tags.all()) == 3)

        tags = [x.title for x in response.context['article'].tags.all()]
        self.assertTrue('tag 1' in tags)
        self.assertTrue('tag 2' in tags)
        self.assertTrue('tag3' in tags)

    def test_update_article_with_tags(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
                'tags_text': 'tag 1, tag 2 ,tag3',
            },
            follow=True)

        self.assertTemplateUsed(response, 'articles/article.html')
        self.assertContains(response, 'New article')

        response = self.client.get('/articles/new-article/edit')

        self.assertContains(response, 'id_tags_text')

        response = self.client.post('/articles/new-article/edit',
            {
                'title': 'New article',
                'body': 'New article body',
                'tags_text': 'tag 1, tag 4, tag 5',
            },
            follow=True)

        self.assertTrue('article' in response.context)
        self.assertTemplateUsed(response, 'articles/article.html')
        tags = [x.title for x in response.context['article'].tags.all()]

        self.assertTrue(len(tags) == 3)
        self.assertTrue('tag 1' in tags)
        self.assertTrue('tag 2' not in tags)
        self.assertTrue('tag 3' not in tags)
        self.assertTrue('tag 4' in tags)
        self.assertTrue('tag 5' in tags)

        # Check the tags appear in the template
        self.assertContains(response, 'tag 1')
        self.assertContains(response, 'tag 4')
        self.assertContains(response, 'tag 5')

    def test_update_article_with_notags(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'New article',
                'body': 'New article body',
                'tags_text': 'tag 1, tag 2 ,tag3',
            },
            follow=True)

        self.assertTemplateUsed(response, 'articles/article.html')
        self.assertContains(response, 'New article')

        response = self.client.get('/articles/new-article/edit')

        self.assertContains(response, 'id_tags_text')
        self.assertContains(response, 'tag 1')
        self.assertContains(response, 'tag 2')
        self.assertContains(response, 'tag3')

        response = self.client.post('/articles/new-article/edit',
            {
                'title': 'New article',
                'body': 'New article body',
                'tags_text': '',
            },
            follow=True)

        self.assertTrue('article' in response.context)
        self.assertContains(response, "Article updated")
        tags = [x.title for x in response.context['article'].tags.all()]

        self.assertTrue(len(tags) == 0)
        self.assertTrue('tag 1' not in tags)
        self.assertTrue('tag 4' not in tags)
        self.assertTrue('tag 5' not in tags)

    def test_tag_view(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'Article 1',
                'body': 'Article body',
                'tags_text': 'tag 1, tag 2, tag 3',
                'published': True,
            },
            follow=True)

        response = self.client.post('/articles/new',
            {
                'title': 'Article 2',
                'body': 'Article body',
                'tags_text': 'tag 2, tag 3',
                'published': True,
            },
            follow=True)

        response = self.client.post('/articles/new',
            {
                'title': 'Article 3',
                'body': 'Article body',
                'tags_text': 'tag 3',
                'published': True,
            },
            follow=True)

        response = self.client.get('/articles/tags/tag-1')
        self.assertContains(response, "Article 1")
        self.assertNotContains(response, "Article 2")
        self.assertNotContains(response, "Article 3")

        response = self.client.get('/articles/tags/tag-2')
        self.assertContains(response, "Article 1")
        self.assertContains(response, "Article 2")
        self.assertNotContains(response, "Article 3")

        response = self.client.get('/articles/tags/tag-3')
        self.assertContains(response, "Article 1")
        self.assertContains(response, "Article 2")
        self.assertContains(response, "Article 3")

        self.assertContains(response, "<h1>tag 3</h1>")

    def test_non_existent_tag_view(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'Article 1',
                'body': 'Article body',
                'tags_text': 'tag 1, tag 2, tag 3',
                'published': True,
            },
            follow=True)

        response = self.client.get('/articles/tags/tag-4')
        self.assertTrue(response.status_code == 404)

    def test_tag_link_on_article(self):
        self.client.login(username="testuser", password="testuser")

        response = self.client.post('/articles/new',
            {
                'title': 'Article 1',
                'body': 'Article body',
                'tags_text': 'tag 1, tag 2, tag 3',
                'published': True,
            },
            follow=True)

        response = self.client.get('/articles/article-1')
        self.assertContains(response, reverse('articles:tag-view', kwargs={'slug': 'tag-1'}))

    def test_popular_tags(self):
        self.client.login(username="testuser", password="testuser")

        tags = {
          'taga': 0,
          'tagb': 0,
          'tagc': 0,
          'tagd': 0,
        }
        for i in range(1, 10):
            text = 'taga'
            tags['taga'] += 1
            if i > 2:
                text = text + ',tagb'
                tags['tagb'] += 1
            if i > 4:
                text = text + ',tagc'
                tags['tagc'] += 1
            if i > 6:
                text = text + ',tagd'
                tags['tagd'] += 1

            response = self.client.post('/articles/new',
                {
                    'title': 'Article %d' % i, 'body': 'Article body',
                    'tags_text': text,
                    'published': True,
                },
                follow=True)

        #print ArticleTag.objects.all()
        #print tags

        # for tag in ArticleTag.objects.all():
        #     print tag.title, tag.article_set.count()

        response = self.client.get('/articles/')
        for t in response.context['popular_tags']:
            if t['tag'].title in tags and t['count'] == tags[t['tag'].title]:
                del tags[t['tag'].title] 

        self.assertTrue(tags == {})

