from django.conf.urls import url
from .views import ArticleListView, ArticleDeleteView, PageView, ArticleView, \
                   ArticleImageCreateView, ArticleImageDeleteView, ArticleImageUpdateView,\
                   ArticleImageView, ArticleImageListView, PageListView, ArticleUpdateView, \
                   ArticleCreateView
import articles.views

urlpatterns = [
    url(r'^$',                                  ArticleListView.as_view(), name='list'),
    url(r'^new$',                               ArticleCreateView.as_view(),  name='new'),
    url(r'^pages/(?P<slug>[a-z0-9\-]+)$',        PageView.as_view(), name='page-view'),
    url(r'^pages/$',                             PageListView.as_view(), name='page-view'),
    url(r'^images/$',                            ArticleImageListView.as_view(), name='image-list'),
    url(r'^images/new$',                         ArticleImageCreateView.as_view(), name='image-new'),
    url(r'^images/(?P<pk>[0-9]+)$',              ArticleImageView.as_view(), name='image-view'),
    url(r'^images/(?P<pk>[0-9]+)/edit$',         ArticleImageUpdateView.as_view(), name='image-edit'),
    url(r'^images/(?P<pk>[0-9]+)/delete$',       ArticleImageDeleteView.as_view(), name='image-delete'),

    url(r'^(?P<slug>[a-z0-9\-]+)$',             ArticleView.as_view(), name='view'),
    url(r'^(?P<slug>[a-z0-9\-]+)/edit$',        ArticleUpdateView.as_view(), name='edit'),
    url(r'^(?P<slug>[a-z0-9\-]+)/delete$',      ArticleDeleteView.as_view(), name='delete'),
]
