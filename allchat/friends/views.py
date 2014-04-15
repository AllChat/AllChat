# -*- coding: utf-8 -*- 
from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupList, FriendList, GroupInfo
from sqlalchemy import and_
from allchat.amqp.Impl_kombu import RPC, cast

class friends_view(MethodView):
    def get(self):
        pass
    def post(self, name):
        if name is None:
            return ("Error in the URL. Please put the account name in the URL.", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            pass
        else:
            return ("Please upload a json data", 403)

    def delete(self, name):
        pass