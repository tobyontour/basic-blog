from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = True

SECRET_KEY = 'SECRET_KEY'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': BASE_DIR + '/db.sqlite',         # Or path to database file if using sqlite3.
    }
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
]

INSTALLED_APPS += ('debug_toolbar',)

MIDDLEWARE = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE

LOGGING['loggers']['articles'] = {
    'handlers': ['console', ],
    'level': 'DEBUG',
    'propagate': True,
}

CACHES = {
    'default': {
#         # 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         # 'LOCATION': os.path.join(BASE_DIR, 'logs/cache'),
#         # 'TIMEOUT': 3600,
#         # 'OPTIONS': {
#         #     'MAX_ENTRIES': 5000,
#         #     'CULL_FREQUENCY': 5,
#         # }
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': [
#             '127.0.0.1:11211',
#         ]
    }
}

ALLOWED_HOSTS = ['127.0.0.1']

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

SECRET_KEY = 'THIS_IS_A_TEST_SECRET_KEY'