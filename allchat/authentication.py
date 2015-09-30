# -*- coding: utf-8 -*-
from flask import request, make_response, session
from allchat.database.sql import get_session
from allchat.database.models import UserAuth
from functools import wraps


def authorized(func):
    @wraps(func)
    def action(*args, **kwargs):
        token = request.headers.get('token', None)
        account = session.get('account', None)
        if token and account:
            db_session = get_session()
            try:
                auth = db_session.query(UserAuth).filter(UserAuth.account == account).one()
            except Exception as e:
                return make_response("Authentication first", 401)
            else:
                if auth.is_token(token) and not auth.is_token_timeout():
                    return func(*args, **kwargs)
        return make_response("Authentication first", 401)
    return action

def checked(func):
    @wraps(func)
    def action(*args, **kwargs):
        name = kwargs.get('name', None)
        account = session.get('account', None)
        if name is not None and name == account:
            return func(*args, **kwargs)
        return make_response('Account error', 403)
    return action
