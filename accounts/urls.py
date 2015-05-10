from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^$',                              'accounts.views.profile',        name='profile'),
    url(r'^user/(?P<username>[a-z]{2,8})$', 'accounts.views.public_profile', name='public_profile'),
    url(r'^register$',                      'accounts.views.register',       name='register'),

    url(r'^login/$',                'django.contrib.auth.views.login',                   name='login'),
    url(r'^logout$',                'django.contrib.auth.views.logout',                  name='logout'),
    url(r'^password_change/$',      'django.contrib.auth.views.password_change',         name='password_change'),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done',    name='password_change_done'),
    url(r'^password_reset/$',       'django.contrib.auth.views.password_reset',          name='password_reset'),
    url(r'^password_reset/done/$',  'django.contrib.auth.views.password_reset_done',     name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                                    'django.contrib.auth.views.password_reset_confirm',  name='password_reset_confirm'),
    url(r'^reset/done/$',           'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
)
