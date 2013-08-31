from __future__ import unicode_literals

import logging

import pymongo

from django.core import signing
from django.conf import settings

from . import models, exceptions

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


def _get_messages_table():
    return pymongo.MongoClient(settings.MONGO_DB_URL).mongodb.default.messages


@event
def authentication_authenticate(connection, token, salt):
    try:
        channel = signing.loads(
            token,
            key=SECRET_KEY,
            salt=salt,
            max_age=settings.CHANNEL_MAX_AGE,
        )
    except (signing.BadSignature, KeyError):
        logging.debug('Authentication error: invalid token')
        raise exceptions.AuthenticationError('Invalid token')
    else:
        connection.channel = channel
        logging.debug('Authentication successful')
        connection.emit(name='authentication:success')


@event
def message_create(connection, author, text, client_id, **kwargs):
    messages = _get_messages_table()
    message_id = messages.insert(dict(
        author=author,
        text=text,
    ))
    new_message = messages.find_one(dict(_id=message_id))

    return dict(
        name='message:created',
        data=dict(
            message=new_message,
            client_id=client_id,
        )
    )

@event
def bootstrap(connection):
    connection.emit(name="message:list", data=list(_get_messages_table().find()))
