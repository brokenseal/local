import os
import dj_database_url

from local.settings import DATABASES

DEBUG = True
DATABASES['default'] = dj_database_url.config()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = ['*']
IO_PORT = 80

CHANNEL_MAX_AGE = 40
DISABLED_TRANSPORTS = ['websocket']

REDIS_URL = None
for _redis_url in ('REDISCLOUD_URL', 'REDISTOGO_URL', 'OPENREDIS_URL'):
    if _redis_url in os.environ:
        REDIS_URL = os.environ[_redis_url]
        break

assert REDIS_URL is not None, "Redis not installed"

MONGO_DB_URL = os.environ['MONGOLAB_URI']
