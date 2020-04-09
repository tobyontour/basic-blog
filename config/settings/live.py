from .base import *

import os, json

with open(BASE_DIR + '/../secrets.json') as f:
    secrets = json.loads(f.read())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': secrets['DB_NAME'],  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': secrets['DB_USER'],
        'PASSWORD': secrets['DB_PASS'],
        'HOST': secrets['DB_HOST'],  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                             # Set to empty string for default.
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
SECRET_KEY = secrets['SECRET_KEY']
