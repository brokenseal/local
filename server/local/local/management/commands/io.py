from __future__ import unicode_literals

import os
import urlparse
from sockjs.tornado import SockJSRouter

import tornadoredis
from tornado import web
from tornado import ioloop

from django.conf import settings
from django.core.management.base import BaseCommand

from local import connections


def on_connected(*args):
    print "args: {}".format(args)


class Command(BaseCommand):
    help = 'Run io server'
    args = '[port]'

    def handle(self, *args, **options):
        redis_connection_url = os.environ.get('REDISTOGO_URL', os.environ.get('OPENREDIS_URL', 'redis://localhost:6379'))
        url = urlparse.urlparse(redis_connection_url)
        pool = tornadoredis.ConnectionPool(host=url.hostname, port=url.port)
        redis_connection = tornadoredis.Client(connection_pool=pool, password=url.password)
        redis_connection.connect()
        redis_connection.psubscribe("*", lambda msg: redis_connection.listen(connections.Connection.pubsub_message))

        # Disable websockets for heroku
        router = SockJSRouter(connections.Connection, '/chat', dict(disabled_transports=['websocket']))
        app = web.Application(router.urls)
        app.listen(os.environ.get("PORT", 8080))
        ioloop.IOLoop.instance().start()
