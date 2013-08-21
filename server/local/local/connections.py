from __future__ import unicode_literals
import json

import pika
import logging
import tornadio2
from pika.adapters.tornado_connection import TornadoConnection
from tornadio2.conn import EventMagicMeta

from .utils import event
from . import models

logger = logging.getLogger(__name__)


class BaseConnectionMetaClass(EventMagicMeta):
    amqp_enabled = False
    amqp_enabled_classes = set()

    def __new__(mcs, name, bases, dictn):
        cls = EventMagicMeta.__new__(mcs, name, bases, dictn)

        # set of unique attributes created on a per class basis
        # set of active connections handled by this connection class
        cls.active_connections = set()

        if cls.amqp_enabled:
            # open connection and channel only for amqp enabled classes
            cls.frame = None
            cls.channel = None
            cls.amqp_connection = None

            mcs.amqp_enabled_classes.add(cls)

        return cls

    @classmethod
    def setup_connections(mcs, io_loop):
        def _setup(*args, **kwargs):
            for cls in mcs.amqp_enabled_classes:
                # setup a single amqp connection, channel and frame for every amqp enabled class instantiated by this
                # meta class
                cls.amqp_connection = TornadoConnection(
                    on_open_callback=cls.on_connection_open,
                    custom_ioloop=io_loop,
                )

        return _setup

    def on_connection_open(cls, amqp_connection):
        # welcome to the callback hell, baby!
        # first jump
        print("New AMQP Connection established")

        cls.channel = cls.amqp_connection.channel(cls.on_channel_open)

    def on_channel_open(cls, channel):
        # second jump
        print("New AMQP Channel opened: {}".format(cls.channel))

        cls.channel.queue_declare(callback=cls.on_queue_declare,
                                  queue="chat",
                                  exclusive=True)

    def on_queue_declare(cls, frame):
        # third jump
        print("AMQP queue declared: {}".format(frame))

        cls.frame = frame
        cls.channel.basic_consume(cls.on_amqp_message,
                                  queue="chat",
                                  exclusive=True)

    def on_amqp_message(cls, channel, method, header, body):
        # fourth jump
        # TODO: improve, this is currently limited to positional arguments only
        args = json.loads(body)

        for connection in cls.active_connections:
            connection.emit(*args)


class BaseConnection(tornadio2.SocketConnection):
    __metaclass__ = BaseConnectionMetaClass

    def on_open(self, request):
        # add this connection to this class' set of active connections
        self.active_connections.add(self)

        print("Connection opened - {}".format(self))

    def on_close(self):
        # remove this connection to this class' set of active connections
        print("Connection closed - {}".format(self))

        self.active_connections.remove(self)

    def broadcast(self, *args, **kwargs):
        if self.channel is None:
            # narrow broadcast on this thread connections only
            for connection in self.active_connections:
                connection.emit(*args)
        else:
            # wide broadcast on all thread connected to the same broker
            # TODO: improve, this is currently limited to positional arguments only
            body = json.dumps(args)

            self.channel.basic_publish(exchange='',
                                       routing_key="chat",
                                       body=body,
                                       properties=pika.BasicProperties(content_type="text/plain", delivery_mode=1))


class ChatConnection(BaseConnection):
    # as of now, this is the only amqp enabled class
    amqp_enabled = True

    @event
    def bootstrap(self):
        # bootstrap client with a list of all messages
        self.emit('bootstrap', list(models.Message.objects.as_dicts()))

    @event
    def message_create(self, **kwargs):
        # create a new message
        new_message = models.Message.objects.create(
            author=kwargs.get('author'),
            text=kwargs.get('text'),
        )

        self.broadcast('message:created', new_message.as_dict(), kwargs.get('clientId'))

    @event
    def stats(self):
        return self.session.server.stats.dump()


class MainConnection(BaseConnection):
    __endpoints__ = {
        '/chat': ChatConnection,
    }

    def on_message(self, message):
        print message
