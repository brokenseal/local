from __future__ import unicode_literals

import json
import logging
import redis

from sockjs.tornado import SockJSConnection

from django.conf import settings

from . import messages

logger = logging.getLogger(__name__)


class MainConnection(SockJSConnection):
    """
    Main SockJSConnection subclass
    Events emitted by this class:
        - authentication:request
        - authentication:success
        - error
    """
    active_connections = set()

    ### class methods
    @classmethod
    def pubsub_message(cls, message):
        """ pub sub callback passed to redis and called on message publication """
        event = json.loads(unicode(message.body))

        for client in cls.active_connections:
            if client.is_authenticated and client.channel == message.channel:
                client.emit(event.name, **event.data)

    def __init__(self, *args, **kwargs):
        # instance properties, set during authentication
        self.channel = None
        self.redis_client = None

        super(MainConnection, self).__init__(*args, **kwargs)

    ### SockJSConnection specific methods
    def send(self, message, binary=False):
        """
        Sends a message to the client
        If the passed in message is dictionary, it dumps it first and then pass it along
        """
        if isinstance(message, dict):
            message = json.dumps(message)

        return super(MainConnection, self).send(message, binary)

    def on_open(self, request):
        """
        Callback fired when a new client connects for the first time
        Request the client to authenticate and add them to client pool.
        """
        self.emit('authentication:request')
        self.active_connections.add(self)
        self.redis_client = redis.Redis()

    def on_message(self, message):
        """
        On message callback
        Fired when a message is received
        """
        try:
            message = json.loads(message)
        except ValueError:
            return self.emit('error', error=dict(
                name='ValueError',
                message='Failed to load message',
            ))

        if not settings.DEBUG and not self.is_authenticated and not message.name == 'authentication:request':
            # the very first message needs to be the authentication request, otherwise this is an unauthorized request
            return self.emit('error', error=dict(
                name='NotAllowed',
                message='Client is not authenticated',
            ))

        return self.on_event(message['name'], **message.data)

    def on_close(self):
        """
        Remove client from pool
        """
        self.active_connections.remove(self)
        self.channel = None
        # close redis client?
        return super(MainConnection, self).on_close()

    ### custom connection methods mainly used to handle socket.io like events style
    def emit(self, name, **kwargs):
        """
        Standard format for all messages
        """
        return self.send(dict(
            name=name,
            data=kwargs,
        ))

    def broadcast_event(self, name, **kwargs):
        self.redis_client.publish('chat', json.dumps(dict(
            name=name,
            data=kwargs,
        )))

    def on_event(self, name, **kwargs):
        if name not in messages.routing:
            return self.emit('error', dict(
                name='UnknownEvent',
                message='Unknown event `{}`'.format(name),
            ))

        event_handler = messages.resolve(name)
        result = event_handler(self, **kwargs)

        if result is not None:
            # automatically broadcast a new message if the event handler returns a value
            return self.broadcast_event(**result)

    @property
    def is_authenticated(self):
        return bool(self.channel)
