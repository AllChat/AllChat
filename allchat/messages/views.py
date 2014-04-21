# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import request, make_response
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, FriendList
from allchat.amqp.Impl_kombu import send_message
from sqlalchemy import and_, or_
import datetime


class messages_view(MethodView):
    def post(self, type):
        content_type = request.environ['CONTENT_TYPE'].split(';', 1)[0]
        tmp = content_type.split(';', 1)[0]
        if tmp == "application/json":
            try:
                if type == "individual":
                    return self.individual_message()
                elif type == "group":
                    return self.individual_message()
                else:
                    return ("Error URL", 403)
            except Exception,e:
                return ("Failed to pass the message", 500)
        else:
            return ("Error Content_Type in the request, please upload a "
                    "application/json request", 403)

    def individual_message(self):
        try:
            para = request.get_json()
        except Exception as e:
            return ("The json data can't be parsed", 403, )
        sender = request.headers['message_sender']
        receiver = request.headers['message_receiver']
        db_session = get_session()
        users = db_session.query(UserInfo).join(FriendList).filter(or_(UserInfo.username == sender,
                                UserInfo.username == receiver)).filter(and_(UserInfo.state != "offline",
                                UserInfo.deleted == False)).all()
        if len(users) != 2:
            return ('Message send failed due to account not exist or offline', 403)
        user_from = None
        user_to = None
        flag = False
        if users[0].username == sender:
            user_from = users[0]
            user_to = users[1]
        else:
            user_from = users[1]
            user_to = users[0]
        for friend in user_from.friends:
            if friend.username == user_to.username and friend.confirmed == True:
                flag = True
                break;
        if not flag:
            return ('Forbidden! The recipient is not your friend.', 403)

        message = dict()
        message['from'] = user_from.username
        message['to'] = user_to.username
        message['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message['msg'] = para['msg']
        ret = send_message(user_from.username, user_to.username, message)
        if not ret:
            return ("Send message successfully", 200)
        else:
            return ret


    def group_message(self):
        pass