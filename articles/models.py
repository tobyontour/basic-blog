import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.
@python_2_unicode_compatible
class Article(models.Model):
    # author
    author = models.ForeignKey(User, editable=False)
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
    article = models.ForeignKey(Article, related_name='images')
    # title
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    # image
    image = models.ImageField(upload_to='articles/%Y/%m/%d')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('articles:image-view', args=[self.pk])
