import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.urls import reverse
from django.utils.text import slugify
from django import forms
from django.core.cache import caches
from django.db.models.signals import post_save, post_delete

cache = caches['default']


class ArticleTag(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, blank=False, unique=True)

    class Meta:
        app_label = 'articles'

    def __str__(self):
        return self.title

    def clean(self):
        self.slug = slugify(self.title)

class Article(models.Model):
    # author
    author = models.ForeignKey(User, editable=False, on_delete=models.SET_NULL, null=True)
    # title
    title = models.CharField(max_length=100)
    subheading = models.CharField(max_length=100, blank=True)
    # body
    body = models.TextField()
    # image
    image = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True)

    slug = models.SlugField(max_length=50, blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    pub_date = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    is_page = models.BooleanField(default=False)
    tags = models.ManyToManyField(ArticleTag, blank=True)

    class Meta:
        app_label = 'articles'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.is_page:
            return reverse('page-view', args=[self.slug])
        else:
            return reverse('articles:view', args=[self.slug])

    def clean(self):
        # Set the pub_date for published items if it hasn't been set already.
        if self.published and self.pub_date is None:
            self.pub_date = datetime.date.today()

        if self.slug == "":
            self.slug = slugify(self.title)

class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug" : ("title",)}

class ArticleImage(models.Model):
    article = models.ForeignKey(Article, related_name='images', on_delete=models.CASCADE)
    # title
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    # image
    image = models.ImageField(upload_to='articles/%Y/%m/%d')

    class Meta:
        app_label = 'articles'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('articles:image-view', args=[self.pk])


# from .models import Article

def menu_for_pages(request):
    '''
    Provides a list of static pages for the menu
    '''
    data = cache.get('menu_for_pages')
    if data is None:
        data = {
            'menu_pages': Article.objects.filter(published=True).filter(is_page=True).exclude(slug__in=['home','articles'])
        }
        cache.set('menu_for_pages', data, 300)
    return data

def articles_changed(sender, **kwargs):
    '''
    Flushes the page cache when a page is saved
    '''
    instance = kwargs['instance']
    if instance.published and instance.is_page and instance.slug not in ['home', 'articles']:
        cache.delete('menu_for_pages')

post_save.connect(articles_changed, sender=Article)
post_delete.connect(articles_changed, sender=Article)
