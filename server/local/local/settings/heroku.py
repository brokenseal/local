import os

CHANNEL_MAX_AGE = 40
DISABLED_TRANSPORTS = ['websocket']

REDIS_URL = None
for _redis_url in ('REDISCLOUD_URL', 'REDISTOGO_URL', 'OPENREDIS_URL'):
    if _redis_url in os.environ:
        REDIS_URL = os.environ[_redis_url]
        break

assert REDIS_URL is not None, "Redis not installed"
