import re
import logging

# Create your views here.
from django import forms
from django.utils.text import slugify
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.decorators.cache import cache_page, never_cache
from django.template import RequestContext, loader
from django.db.models import Count
from django.forms import ModelForm

from django.core.cache import caches

from django.utils.text import slugify
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, UpdateView, CreateView, FormView
from django.utils import timezone
from django.conf import settings
from django.forms.formsets import formset_factory
from django.forms.models import modelform_factory

from braces.views import LoginRequiredMixin

from articles.forms import ArticleForm, ArticleImageForm
from articles.models import Article, ArticleImage, ArticleTag

logger = logging.getLogger(__name__)

cache = caches['default']

def _get_images_in_text(text):
    m = re.findall(r"\{image:(?P<image_number>\d+)\}", text)
    ret = []
    for number in m:
        ret.append(int(number))
    return ret

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'subheading', 'body', 'image', 'slug', 'published', 'is_page')

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            tags = ", ".join([x.title for x in self.instance.tags.all()])
        else:
            tags = ""
        self.fields['tags_text'] = forms.CharField(label="Tags", required=False, initial=tags)

    def clean_tags_text(self):
        raw = self.cleaned_data['tags_text']

        csv = []
        for tag in raw.split(','):
            if len(tag.strip()) > 0:
                csv.append(tag.strip())

        # Deduplicate
        self.cleaned_data['tags_text'] = list(set(csv))
        return self.cleaned_data['tags_text']

    def save(self, force_insert=False, force_update=False, commit=True):
        article = super(ArticleForm, self).save(commit=True)  # have to save to access article.tags

        # Get the tags we want
        tags_text_list = self.cleaned_data['tags_text']

        # See which ones exist
        tags = ArticleTag.objects.filter(title__in=tags_text_list)

        # Start from scratch
        article.tags.clear()

        # Add existing tags
        for tag in tags:
            article.tags.add(tag.pk)

        # Create new ones
        for tag in tags_text_list:
            if tag not in [t.title for t in tags]:
                # Create tag
                article.tags.create(title=tag, slug=slugify(tag))

        if commit:
            article.save()
        return article

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, 'Article saved')
        form.instance.author = self.request.user
        return super(ArticleCreateView, self).form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    template_name = 'articles/article_form.html'
    form_class = ArticleForm
    # fields = ['title', 'subheading', 'body','image','slug','published','is_page', 'tags']
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super(ArticleUpdateView, self).get_context_data(**kwargs)
        context['header_image'] = context[self.context_object_name].image
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, 'Article updated')
        return super(ArticleUpdateView, self).form_valid(form)

class ArticleView(DetailView):
    template_name = 'articles/article.html'
    model = Article
    context_object_name = 'article'

    def get_queryset(self):
        queryset = super(ArticleView, self).get_queryset()

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(published=True)

        return queryset.filter(is_page=False)

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data( **kwargs)
        image_ids = _get_images_in_text(context[self.context_object_name].body)
        if len(image_ids) > 0:
            objs = ArticleImage.objects.filter(pk__in=image_ids)
            images = {}
            for i in objs:
                images[i.pk] = i

        body = context[self.context_object_name].body
        for i in image_ids:
            body = body.replace('{image:%d}' % i, '![%s](%s)' % (images[i].title, images[i].image.url))

        context['body'] = body
        context['header_image'] = context[self.context_object_name].image
        return context

class PageView(DetailView):
    template_name = 'articles/page.html'
    model = Article
    context_object_name = 'page'

    def get_queryset(self):
        queryset = super(PageView, self).get_queryset()

        return queryset.filter(is_page=True).filter(published=True)

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data( **kwargs)
        context['header_image'] = context[self.context_object_name].image
        return context

class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    success_url = reverse_lazy('articles:list')
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super(ArticleDeleteView, self).get_context_data( **kwargs)

        context['header_image'] = context[self.context_object_name].image
        return context

class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = super(ArticleListView, self).get_queryset()

        return queryset.filter(is_page=False).filter(published=True)

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        page = Article.objects.filter(slug='articles').filter(published=True).filter(is_page=True)
        if len(page) > 0:
             context['page'] = page[0]
             context['header_image'] = page[0].image

        logger.warn("Horribly inefficient query here")
        pt = cache.get('popular_tags')
        if pt is None:
            pt = []
            for tag in ArticleTag.objects.all():
                pt.append({
                    'tag': tag,
                    'count': tag.article_set.count()
                    })
            cache.set('popular_tags', pt, 3600)
        context['popular_tags'] = pt

        return context

class PageListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = super(PageListView, self).get_queryset()

        return queryset.filter(is_page=True)

class HomePageView(ListView):
    model = Article
    template_name = 'home.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = super(HomePageView, self).get_queryset()

        return queryset.filter(is_page=False).filter(published=True)[:5]

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        home_article = Article.objects.filter(slug='home').filter(published=True).filter(is_page=True)
        if len(home_article) > 0:
            context['home_article'] = home_article[0]
            context['header_image'] = home_article[0].image

        return context

class ArticleImageCreateView(LoginRequiredMixin, CreateView):
    model = ArticleImage
    template_name = 'articles/article_image_form.html'
    fields = ['image', 'title', 'article']

class ArticleImageUpdateView(LoginRequiredMixin, UpdateView):
    model = ArticleImage
    template_name = 'articles/article_image_form.html'
    fields = ['title']
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        context = super(ArticleImageUpdateView, self).get_context_data(**kwargs)
        context['header_image'] = context[self.context_object_name].image
        return context

class ArticleImageListView(LoginRequiredMixin, ListView):
    model = ArticleImage
    template_name = 'articles/article_image_list.html'
    context_object_name = 'images'

    def get_queryset(self):
        queryset = super(ArticleImageListView, self).get_queryset()

        return queryset.order_by('-pk')

class ArticleImageView(DetailView):
    template_name = 'articles/article_image.html'
    model = ArticleImage
    context_object_name = 'image'

class ArticleImageDeleteView(LoginRequiredMixin, DeleteView):
    model = ArticleImage
    success_url = reverse_lazy('articles:image-list')
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        context = super(ArticleImageDeleteView, self).get_context_data( **kwargs)

        context['header_image'] = context[self.context_object_name].image
        return context

class ArticleTagView(ListView):
    model = Article
    template_name = 'articles/tag.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = super(ArticleTagView, self).get_queryset()
        return queryset.filter(tags__slug=self.kwargs['slug']).filter(is_page=False).filter(published=True)

    def get_context_data(self, **kwargs):
        context = super(ArticleTagView, self).get_context_data(**kwargs)
        context['tag'] = get_object_or_404(ArticleTag, slug=self.kwargs['slug'])

        return context