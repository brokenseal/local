from __future__ import unicode_literals

import logging

from django.core import signing
from django.conf import settings

from . import models

SECRET_KEY = "test"

routing = {}
logger = logging.getLogger(__name__)


def resolve(name):
    return routing[name]


def event(message_or_func):
    if callable(message_or_func):
        message = ':'.join(message_or_func.__name__.split('_'))
        routing[message] = message_or_func
        return message_or_func

    def _wrapper(func):
        routing[message_or_func] = func
        return func

    return _wrapper


@event
def authentication_authenticate(connection, token, salt):
    try:
        channel = signing.loads(
            token,
            key=SECRET_KEY,
            salt=salt,
            max_age=settings.CHANNEL_MAX_AGE,
        )
    except (signing.BadSignature, KeyError) as e:
        logging.debug('Authentication error: invalid token')
        connection.emit('error', name='AuthenticationError', message='Invalid token')
    else:
        connection.channel = channel
        logging.debug('Authentication successful')
        connection.emit(name='authentication:success')


@event
def message_create(connection, author, text, client_id):
        new_message = models.Message.objects.create(
            author=author,
            text=text,
        )

        return dict(
            name='message:created',
            data=dict(
                message=new_message.as_dict(),
                client_id=client_id,
            )
        )

@event
def bootstrap(connection, data):
    return dict(
        name="message:list",
        data=list(models.Message.objects.as_dicts()),
    )
