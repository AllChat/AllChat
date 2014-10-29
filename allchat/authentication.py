# -*- coding: utf-8 -*-
from flask import request, make_response
def authorized(func):
    try:
        token = request.headers['token']
    except Exception,e:
        return make_response("Authentication first", 401)

    def action(*args, **kwargs):
        func(*args, **kwargs)
    return action
