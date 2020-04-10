from django.conf.urls import include, url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from articles.views import PageView, HomePageView, PageListView
admin.autodiscover()

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),

    # Authentication
    # url(r'^accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    # path('articles/', include('articles.urls')),
    path('articles/', include(('articles.urls', 'articles'), namespace='articles')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url('admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url('pages/$', PageListView.as_view(), name='page-view'),
    url(r'^(?P<slug>[0-9a-z-]+)$', PageView.as_view(), name='page-view'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
