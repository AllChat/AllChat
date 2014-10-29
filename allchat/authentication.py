# -*- coding: utf-8 -*-
from flask import request, make_response, session
from allchat.database.sql import get_session
from allchat.database.models import UserAuth
def authorized(func):
    def action(*args, **kwargs):
        return func(*args, **kwargs)
    def failed(*args, **kwargs):
        return make_response("Authentication first", 401)
    try:
        token = request.headers['token']
    except Exception,e:
        return failed
    else:
        db_session = get_session()
        try:
            auth =db_session.query(UserAuth).filter(UserAuth.account == session['account']).one()
        except Exception,e:
            return failed
        else:
            if not auth.is_token(token) or auth.is_token_timeout():
                return failed
    return action
