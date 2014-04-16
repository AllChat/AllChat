# -*- coding: utf-8 -*- 
from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupMember, FriendList, GroupInfo
from sqlalchemy import and_
from allchat.amqp.Impl_kombu import RPC, cast
from flask import json

class friends_view(MethodView):
    def get(self):
        pass
    def post(self, name):
        if name is None:
            return ("Error in the URL. Please put the account name in the URL.", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            db_session = get_session()
            try:
                req_user = db_session.query(UserInfo).filter(and_(UserInfo.username == name,
                                        UserInfo.deleted == False, UserInfo.state != 'offline')).one()
            except Exception, e:
                return ("The account {account} is not exist or offline".format(account = name), 404)
            else:
                try:
                    resp_user = db_session.query(UserInfo).filter(and_(UserInfo.username == para['account'],
                                        UserInfo.deleted == False)).one()
                except Exception,e:
                    return ("The user {account} being added doesn't exist".format(account = para['account']), 404)
                else:
                    message = dict()
                    message['method'] = "add_friend_req"
                    tmp = dict()
                    tmp['from'] = req_user.username
                    tmp['to'] = resp_user.username
                    tmp['msg'] = para['message']
                    message['para'] = tmp
                    cnn = RPC.create_connection()
                    sender = RPC.create_producer(req_user.username, cnn)
                    try:
                        cast(sender, json.dumps(message), resp_user.username)
                    except:
                        RPC.release_producer(req_user.username)
                        RPC.release_connection(cnn)
                        return ("Added friend failed due to system error", 500)
                    RPC.release_producer(req_user.username)
                    RPC.release_connection(cnn)
                    friend = FriendList(resp_user.username, False)
                    req_user.friends.append(friend)
                    db_session.add(req_user)
                    try:
                        db_session.commit()
                    except:
                        db_session.rollback()
                        return ("DataBase Failed", 503, )
                    else:
                        return ("Have sent add request to {user}".format(user = resp_user.username), 200)
        else:
            return ("Please upload a json data", 403)

    def delete(self, name):
        pass

    def put(self, name):
        if name is None:
            return ("Error in the URL. Please put the account name in the URL.", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception,e:
                return ("The json data can't be parsed", 403, )
            db_session = get_session()
            try:
                req_user = db_session.query(UserInfo).filter(and_(UserInfo.username == name,
                                        UserInfo.deleted == False, UserInfo.state != 'offline'))
            except Exception,e:
                return ("The account {account} is not exist or offline".format(account = name), 404)
            else:
                try:
                    resp_user = db_session.query(UserInfo).join(FriendList).filter(
                                            and_(UserInfo.username == para['account'],UserInfo.deleted == False,
                                                FriendList.username == name, FriendList.confirmed == False)).one()
                except Exception,e:
                    return ("Can't invoke the API before someone request to add you as a friend", 403)
                else:
                    message = dict()
                    message['method'] = "add_friend_resp"
                    tmp = dict()
                    tmp['from'] = req_user.username
                    tmp['to'] = resp_user.username
                    if para['result'] == 'accept':
                        req_user.friends.append(FriendList(para['account'], True))
                        tmp['msg'] = 'accept'
                    elif para['result'] == 'reject':
                        tmp['msg'] = 'reject'
                    message['para'] = tmp
                    db_session.add(req_user)
                    try:
                        db_session.commit()
                    except:
                        db_session.rollback()
                        return ("DataBase Failed", 503, )
                    else:
                        ret = send_message(req_user.username, resp_user.username, message)
                        if not ret:
                            return ("You have confirmed to add {account} as your friend".format(resp_user.username), 200)
                        else:
                            return ret
        else:
            return ("Please upload a json data", 403)


def send_message(req_user, resp_user, message):
    cnn = RPC.create_connection()
    sender = RPC.create_producer(req_user, cnn)
    try:
        cast(sender, json.dumps(message), resp_user)
    except:
        RPC.release_producer(req_user.username)
        RPC.release_connection(cnn)
        return ("Added friend failed due to system error", 500)
    RPC.release_producer(req_user.username)
    RPC.release_connection(cnn)
    return None