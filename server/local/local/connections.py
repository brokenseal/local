from __future__ import unicode_literals

import sys
import uuid
import json
import redis
import logging

from sockjs.tornado import SockJSConnection

from django.conf import settings

from . import messages
from . import exceptions

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
#            if client.is_authenticated and client.channel == message.channel:
            client.emit(**event)

    def __init__(self, *args, **kwargs):
        # instance properties, set during authentication
        self.channel = None
        self.redis_client = None
        self.id = uuid.uuid4()

        super(MainConnection, self).__init__(*args, **kwargs)

    ### SockJSConnection specific methods
    def send(self, message, binary=False):
        """
        Sends a message to the client
        If the passed in message is dictionary, it dumps it first and then pass it along
        """
        return super(MainConnection, self).send(message, binary)

    def on_open(self, request):
        """
        Callback fired when a new client connects for the first time
        Request the client to authenticate and add them to client pool.
        """
        self.emit(name='authentication:request')
        self.active_connections.add(self)

        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)

    def on_message(self, message):
        """
        On message callback
        Fired when a message is received
        """
        try:
            message = json.loads(message)
        except ValueError:
            return self.emit(dict(
                name='error',
                data=dict(
                    name='ValueError',
                    message='Failed to load message',
                )
            ))

        if not settings.DEBUG and not self.is_authenticated and not message['name'] == 'authentication:request':
            # the very first message needs to be the authentication request, otherwise this is an unauthorized request
            self.handle_error(exceptions.NotAllowed('Client is not authenticated'))

        try:
            self.on_event(message['name'], message.get('data', {}))
        except Exception as e:
            self.handle_error(e)
            sys.stderr.write(e.message)

    def handle_error(self, exception):
        self.emit(
            name='error',
            data=dict(
                name=exception.__class__.__name__,
                message=exception.message,
            )
        )

    def on_close(self):
        """
        Remove client from pool
        """
        self.active_connections.remove(self)
        self.channel = None
        # close redis client?
        return super(MainConnection, self).on_close()

    ### custom connection methods mainly used to handle socket.io like events style
    def emit(self, **kwargs):
        """
        Standard format for all messages
        """
        return self.send(kwargs)

    def broadcast_event(self, **kwargs):
        self.redis_client.publish('chat', json.dumps(kwargs))

    def on_event(self, name, data):
        if name not in messages.routing:
            return self.emit(dict(
                name='error',
                data=dict(
                    name='UnknownEvent',
                    message='Unknown event `{}`'.format(name),
                ),
            ))

        event_handler = messages.resolve(name)
        result = event_handler(self, **data)

        if result is not None:
            # automatically broadcast a new message if the event handler returns a dictionary
            return self.broadcast_event(**result)

    @property
    def is_authenticated(self):
        return bool(self.channel)
