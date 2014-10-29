# -*- coding: utf-8 -*-
from flask import request, make_response, session
from allchat.database.sql import get_session
from allchat.database.models import UserAuth


def authorized(func):
    def action(*args, **kwargs):
        try:
            token = session['token']
            account = session['account']
        except Exception,e:
            return make_response("Authentication first", 401)
        else:
            db_session = get_session()
            try:
                auth =db_session.query(UserAuth).filter(UserAuth.account == account).one()
            except Exception,e:
                return make_response("Authentication first", 401)
            else:
                if not auth.is_token(token) or auth.is_token_timeout():
                    return make_response("Authentication first", 401)
                else:
                    return func(*args, **kwargs)
    return action

def checked(func):
    def action(*args, **kwargs):
        try:
            name = kwargs['name']
            account = session['account']
        except Exception,e:
            return func(*args, **kwargs)
        else:
            if name == account:
                return func(*args, **kwargs)
            else:
                return make_response('Account error', 403)
    return action
