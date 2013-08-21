from __future__ import unicode_literals

import tornadio2
from tornado import web

from django.conf import settings
from django.core.management.base import BaseCommand

from local import connections


def on_connected(*args):
    print "args: {}".format(args)


class Command(BaseCommand):
    help = 'Run TornadIO2 server'
    args = '[port]'

    def handle(self, *args, **options):
        if args:
            port = args[0]
        else:
            port = settings.TORNADIO_PORT

        router = tornadio2.TornadioRouter(connections.MainConnection)
        application = web.Application(
            router.urls,
            default_host="0.0.0.0",
            socket_io_port=port,
        )

        io_server = tornadio2.SocketServer(application, auto_start=False)
        io_server.io_loop.add_timeout(100, connections.BaseConnectionMetaClass.setup_connections(io_server.io_loop))

        # start the io loop
        io_server.io_loop.start()
