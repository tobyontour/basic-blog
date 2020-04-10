from .base import *

import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': BASE_DIR + '/db.test.sqlite',         # Or path to database file if using sqlite3.
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/../debug.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

STATIC_ROOT = BASE_DIR + '/../public/static/'
MEDIA_ROOT = BASE_DIR + '/../public/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('SECRET_KEY')

MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)