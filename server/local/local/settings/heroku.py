import dj_database_url

DATABASES = {
    'default':  dj_database_url.config()
}
CHANNEL_MAX_AGE = 10
DISABLED_TRANSPORTS = ['websocket']
