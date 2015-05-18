import re

# Create your views here.
from django import forms
from django.utils.text import slugify
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, render
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.decorators.cache import cache_page, never_cache
from django.template import RequestContext, loader
from django.db.models import Count

from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, UpdateView, CreateView, FormView
from django.utils import timezone
from django.conf import settings
from django.forms.formsets import formset_factory

from braces.views import LoginRequiredMixin

from articles.forms import ArticleForm, ArticleImageForm
from articles.models import Article, ArticleImage

def _get_images_in_text(text):
    m = re.findall(r"\{image:(?P<image_number>\d+)\}", text)
    ret = []
    for number in m:
        ret.append(int(number))
    return ret


@never_cache
@login_required
def article_add(request):
    if request.method == 'POST':

        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            if 'slug' not in request.POST or request.POST['slug'] == "":
                article.slug = slugify(article.title)
            article.author = request.user
            article.save()
            messages.add_message(request, messages.INFO, 'Article saved')
            return HttpResponseRedirect(article.get_absolute_url())

    else:
        form = ArticleForm()

    t = loader.get_template('articles/article_form.html')
    c = RequestContext(request, {'form': form})
    return HttpResponse(t.render(c))

@never_cache
@login_required
def article_edit(request, slug):
    if request.method == 'POST':
        try:
            article = Article.objects.get(slug=slug)
        except DoesNotExist:
            return HttpResponseNotFound
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            if form.has_changed():
                article.save()
            return HttpResponseRedirect(article.get_absolute_url())
    else:
        article = get_object_or_404(Article, slug=slug)
        form = ArticleForm(instance=article)

    t = loader.get_template('articles/article_form.html')
    c = RequestContext(request, {'form': form, 'article': article, 'header_image': article.image})
    return HttpResponse(t.render(c))

class ArticleView(DetailView):
    template_name = 'articles/article.html'
    model = Article
    context_object_name = 'article'

    def get_queryset(self):
        queryset = super(ArticleView, self).get_queryset()

        if not self.request.user.is_authenticated():
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
        return context

class PageListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = super(PageListView, self).get_queryset()

        return queryset.filter(is_page=True)

    def get_context_data(self, **kwargs):
        context = super(PageListView, self).get_context_data(**kwargs)
        return context

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

    # def __init__(self, *args, **kwargs):
    #     super(ArticleImageCreateView, self).__init__(*args, **kwargs)
    #     print self.fields
    #     self.fields['article'].queryset = Article.objects.order_by('-modified')

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

    # def get_context_data(self, **kwargs):
    #     context = super(ArticleListView, self).get_context_data(**kwargs)
    #     return context

class ArticleImageView(DetailView):
    template_name = 'articles/article_image.html'
    model = ArticleImage
    context_object_name = 'image'

class ArticleImageDeleteView(LoginRequiredMixin, DeleteView):
    model = ArticleImage
    success_url = reverse_lazy('articles:images-list')
    context_object_name = 'image'

    def get_context_data(self, **kwargs):
        context = super(ArticleImageDeleteView, self).get_context_data( **kwargs)

        context['header_image'] = context[self.context_object_name].image
        return context
