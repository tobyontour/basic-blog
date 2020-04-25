from django.urls import path
from . import views
from haystack.views import SearchView
from django.conf.urls import url

urlpatterns = [
    path('', views.SiteSearchView.as_view(), name="haystack_search"),
]
