# -*- coding: utf-8 -*-
"""
    flask.ext.security.confirmable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Flask-Security confirmable module

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""

from datetime import datetime

from itsdangerous import BadSignature, SignatureExpired
from flask import current_app as app, request, url_for
from werkzeug.local import LocalProxy

from .exceptions import UserNotFoundError, ConfirmationError
from .utils import send_mail, get_max_age, md5, get_message
from .signals import user_confirmed, confirm_instructions_sent


# Convenient references
_security = LocalProxy(lambda: app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)


def send_confirmation_instructions(user, token):
    """Sends the confirmation instructions email for the specified user.

    :param user: The user to send the instructions to
    """
    url = url_for('flask_security.confirm_account', token=token)

    confirmation_link = request.url_root[:-1] + url

    ctx = dict(user=user, confirmation_link=confirmation_link)

    send_mail('Please confirm your email', user.email,
              'confirmation_instructions', ctx)

    confirm_instructions_sent.send(user, app=app._get_current_object())

    return True


def generate_confirmation_token(user):
    """Generates a unique confirmation token for the specified user.

    :param user: The user to work with
    """
    data = [user.id, md5(user.email)]
    return _security.confirm_serializer.dumps(data)


def should_confirm_email(fn):
    """Handy decorator that returns early if confirmation should not occur."""
    def wrapped(*args, **kwargs):
        if _security.confirmable:
            return fn(*args, **kwargs)
        return False
    return wrapped


@should_confirm_email
def requires_confirmation(user):
    """Returns `True` if the user requires confirmation."""
    return user.confirmed_at == None


def confirm_by_token(token):
    """Confirm the user given the specified token. If the token is invalid or
    the user is already confirmed a `ConfirmationError` error will be raised.
    If the token is expired a `TokenExpiredError` error will be raised.

    :param token: The user's confirmation token
    """
    serializer = _security.confirm_serializer
    max_age = get_max_age('CONFIRM_EMAIL')

    try:
        data = serializer.loads(token, max_age=max_age)
        user = _datastore.find_user(id=data[0])

        if md5(user.email) != data[1]:
            raise UserNotFoundError()

        if user.confirmed_at:
            raise ConfirmationError(get_message('ALREADY_CONFIRMED'))

        user.confirmed_at = datetime.utcnow()
        _datastore._save_model(user)

        user_confirmed.send(user, app=app._get_current_object())

        return user

    except SignatureExpired:
        sig_okay, data = serializer.loads_unsafe(token)
        raise ConfirmationError('Confirmation token expired',
                                user=_datastore.find_user(id=data[0]))

    except BadSignature:
        raise ConfirmationError(get_message('INVALID_CONFIRMATION_TOKEN'))

    except UserNotFoundError:
        raise ConfirmationError(get_message('INVALID_CONFIRMATION_TOKEN'))


def reset_confirmation_token(user):
    """Resets the specified user's confirmation token and sends the user
    an email with instructions explaining next steps.

    :param user: The user to work with
    """
    token = generate_confirmation_token(user)

    user.confirmed_at = None
    _datastore._save_model(user)

    send_confirmation_instructions(user, token)

    return token
