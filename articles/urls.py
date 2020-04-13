from django.urls import path
from . import views

urlpatterns = [
    path('',                                   views.ArticleListView.as_view(), name='list'),
    path('new',                                views.ArticleCreateView.as_view(),  name='new'),
    path('pages/<slug:slug>',                  views.PageView.as_view(), name='page-view'),
    path('pages/',                            views.PageListView.as_view(), name='page-view'),
    path('images/',                           views.ArticleImageListView.as_view(), name='image-list'),
    path('images/new',                        views.ArticleImageCreateView.as_view(), name='image-new'),
    path('images/<int:pk>',             views.ArticleImageView.as_view(), name='image-view'),
    path('images/<int:pk>/edit',        views.ArticleImageUpdateView.as_view(), name='image-edit'),
    path('images/<int:pk>/delete',      views.ArticleImageDeleteView.as_view(), name='image-delete'),

    path('tags/<slug:slug>',        views.ArticleTagView.as_view(), name='tag-view'),

    path('<slug:slug>',             views.ArticleView.as_view(), name='view'),
    path('<slug:slug>/edit',        views.ArticleUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete',      views.ArticleDeleteView.as_view(), name='delete'),
]
