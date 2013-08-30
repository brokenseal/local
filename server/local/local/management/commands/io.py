from __future__ import unicode_literals

import os
import sys
import urlparse

import tornadoredis
from tornado import web
from tornado import ioloop
from sockjs.tornado import SockJSRouter

from django.conf import settings
from django.core.management.base import BaseCommand

from local import connections

DISABLED_TRANSPORTS = getattr(settings, 'DISABLED_TRANSPORTS', [])
IO_PORT = os.environ.get("PORT", settings.IO_PORT)


class Command(BaseCommand):
    help = 'Run io server'
    args = '[port]'

    def handle(self, *args, **options):
        # connect to redis
        url = urlparse.urlparse(settings.REDIS_URL)
        pool = tornadoredis.ConnectionPool(host=url.hostname, port=url.port)
        redis_connection = tornadoredis.Client(connection_pool=pool, password=url.password)
        redis_connection.connect()
        sys.stdout.write("\nConnected to Redis ({}) \n".format(url))
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
        sys.stdout.write("\nApp listening at port {}\n".format(IO_PORT))
        sys.stdout.flush()
        ioloop.IOLoop.instance().start()
