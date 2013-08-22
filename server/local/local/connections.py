from __future__ import unicode_literals

import json
import logging

from sockjs.tornado import SockJSConnection

from django.core import signing

logger = logging.getLogger(__name__)


class Connection(SockJSConnection):
    clients = set()

    @classmethod
    def pubsub_message(cls, msg):
        for client in cls.clients:
            if client.authenticated and client.channel == msg.channel:
                client.send(msg.body)

    def send_error(self, message, error_type=None):
        """
        Standard format for all errors
        """
        return self.send(json.dumps({
            'data_type': 'error' if not error_type else '%s_error' % error_type,
            'data': {
                'message': message
            }
        }))

    def send_message(self, message, data_type):
        """
        Standard format for all messages
        """
        return self.send(json.dumps({
            'data_type': data_type,
            'data': message,
        }))

    def on_open(self, request):
        """
        Request the client to authenticate and add them to client pool.
        """
        self.authenticated = False
        self.channel = None
        self.send_message({}, 'request_auth')
        self.clients.add(self)

    def on_message(self, msg):
        """
        Handle authentication and notify the client if anything is not ok,
        but don't give too many details
        """
        try:
            message = json.loads(msg)
        except ValueError:
            self.send_error("Invalid JSON")
            return

        if message['data_type'] == 'auth' and not self.authenticated:
            try:
                channel = signing.loads(
                    message['data']['token'],
                    key=SECRET_KEY,
                    salt=message['data']['salt'],

                    # Long time out for heroku idling processes.
                    # For other cases, reduce to 10
                    max_age=40,
                )
            except (signing.BadSignature, KeyError) as e:
                self.send_error("Token invalid", 'auth')
                return

            self.authenticated = True
            self.channel = channel
            self.send_message({'message': 'success'}, 'auth')
            logging.debug("Client authenticated for %s" % channel)
        else:
            self.send_error("Invalid data type %s" % message['data_type'])
            logging.debug("Invalid data type %s" % message['data_type'])

    def on_close(self):
        """
        Remove client from pool. Unlike Socket.IO connections are not
        re-used on e.g. browser refresh.
        """
        self.clients.remove(self)
        return super(Connection, self).on_close()
