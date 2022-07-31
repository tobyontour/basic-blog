from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views
from django.conf import settings
import accounts.views


urlpatterns = [
    url(r'^$',                        accounts.views.redirect_view,        name='redirect'),
    url(r'^profile',                accounts.views.profile,        name='profile'),
    url(r'^user/(?P<username>[a-z]{2,8})$', accounts.views.public_profile, name='public_profile'),
    # url(r'^register$',            accounts.views.register,       name='register'),


    url(r'^login/$',                views.LoginView.as_view(),                   name='login'),
    url(r'^logout$',                views.LogoutView.as_view(),                  name='logout'),
    url(r'^password_change/$',      views.PasswordChangeView.as_view(),         name='password_change'),
    url(r'^password_change/done/$', views.PasswordChangeDoneView.as_view(),    name='password_change_done'),
    url(r'^password_reset/$',       views.PasswordResetView.as_view(),          name='password_reset'),
    url(r'^password_reset/done/$',  views.PasswordResetDoneView.as_view(),     name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        views.PasswordResetConfirmView.as_view(),  name='password_reset_confirm'),
    url(r'^reset/done/$',           views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.ALLOW_REGISTRATION:
    urlpatterns = urlpatterns + [url(r'^register$', accounts.views.register, name='register')]