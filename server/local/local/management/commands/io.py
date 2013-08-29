from __future__ import unicode_literals

import os
import sys
import urlparse
from sockjs.tornado import SockJSRouter

import tornadoredis
from tornado import web
from tornado import ioloop

from django.conf import settings
from django.core.management.base import BaseCommand

from local import connections

REDIS_CONNECTION_URL = os.environ.get('REDISTOGO_URL', os.environ.get('OPENREDIS_URL', settings.REDIS_URL))
DISABLED_TRANSPORTS = getattr(settings, 'DISABLED_TRANSPORTS', [])
IO_PORT = os.environ.get("PORT", settings.IO_PORT)


class Command(BaseCommand):
    help = 'Run io server'
    args = '[port]'

    def handle(self, *args, **options):
        # connect to redis
        url = urlparse.urlparse(REDIS_CONNECTION_URL)
        pool = tornadoredis.ConnectionPool(host=url.hostname, port=url.port)
        redis_connection = tornadoredis.Client(connection_pool=pool, password=url.password)
        redis_connection.connect()
        sys.stdout.write("Connected to Redis ({})".format(url))
        redis_connection.psubscribe("*",
                                    lambda message: redis_connection.listen(connections.MainConnection.pubsub_message))

        # enable sockjs routing
        router = SockJSRouter(
            connections.MainConnection,
            '/chat',
            dict(disabled_transports=DISABLED_TRANSPORTS),
        )
        app = web.Application(
            router.urls,
            "0.0.0.0",
        )
        app.listen(IO_PORT)
        sys.stdout.write("App listening at port {}".format(IO_PORT))
        sys.stdout.flush()
        sys.stdout.flush()
        ioloop.IOLoop.instance().start()
