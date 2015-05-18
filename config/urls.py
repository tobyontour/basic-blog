from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from articles.views import PageView, HomePageView, PageListView
admin.autodiscover()

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),

    # Authentication
    url(r'^accounts/', include('accounts.urls')),
    url(r'^articles/', include('articles.urls', namespace='articles')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^pages/$', PageListView.as_view(), name='page-view'),
    url(r'^(?P<slug>[0-9a-z-]+)$', PageView.as_view(), name='page-view'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
