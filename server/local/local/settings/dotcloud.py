from __future__ import unicode_literals

import os

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'local',
        'USER': os.environ['DOTCLOUD_DB_SQL_LOGIN'],
        'PASSWORD': os.environ['DOTCLOUD_DB_SQL_PASSWORD'],
        'HOST': os.environ['DOTCLOUD_DB_SQL_HOST'],
        'PORT': int(os.environ['DOTCLOUD_DB_SQL_PORT']),
    }
}

MEDIA_ROOT = "/home/dotcloud/data"
STATIC_ROOT = "/home/dotcloud/volatile/static"
STATIC_FILES_STORAGE = "django.contrib.staticfiles.storage.CachedStaticFilesStorage"

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '{0}:{1}'.format(os.environ['DOTCLOUD_CACHE_REDIS_HOST'], os.environ['DOTCLOUD_CACHE_REDIS_PORT']),
        'OPTIONS': {
            'DB': 1,
            'PASSWORD': os.environ['DOTCLOUD_CACHE_REDIS_PASSWORD'],
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
    },
}

# we are going to use redis for our session cache as well
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': '/var/log/supervisor/local.log',
            'maxBytes': 1024*1024*25, # 25 MB
            'backupCount': 5,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        # Catch All Logger -- Captures any other logging
        '': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}