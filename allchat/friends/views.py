# -*- coding: utf-8 -*- 
from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupMember, FriendList, GroupInfo
from sqlalchemy import and_
from allchat.amqp.Impl_kombu import RPC, cast, send_message
from flask import json, jsonify

class friends_view(MethodView):
    def get(self, name):
        if name is None:
            return ('URL error', 403)
        db_session = get_session()
        try:
            user = db_session.query(UserInfo).filter(UserInfo.username == name).\
                        filter(UserInfo.deleted == False).filter(UserInfo.state != 'offline').one()
        except Exception,e:
            return ("DataBase Failed", 503, )
        resp = {}
        resp['friendlist'] = []
        for tmp in user.friends:
            if not tmp.confirmed:
                continue
            tmp_user = dict()
            tmp_user['account'] = tmp.username
            tmp_user['nickname'] = tmp.nickname
            tmp_user['state'] = tmp.state
            resp['friendlist'].append(tmp_user)
        return jsonify(resp)

    def post(self, name):
        if name is None:
            return ("Error in the URL. Please put the account name in the URL.", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            if name == para['account'] :
                return ("Can't add yourself as a friend", 403)
            db_session = get_session()
            try:
                req_user = db_session.query(UserInfo).with_lockmode('read').filter(and_(UserInfo.username == name,
                                    UserInfo.deleted == False, UserInfo.state != 'offline')).one()
            except Exception, e:
                return ("The account {account} is not exist or offline".format(account = name), 404)
            else:
                try:
                    resp_user = db_session.query(UserInfo).with_lockmode('read').filter(
                                    and_(UserInfo.username == para['account'],UserInfo.deleted == False)).one()
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
                        db_session.rollback()
                        return ("Added friend failed due to system error", 500)
                    RPC.release_producer(req_user.username)
                    RPC.release_connection(cnn)
                    friend = FriendList(resp_user.username, resp_user.nickname, resp_user.state, False)
                    req_user.friends.append(friend)
                    db_session.begin()
                    try:
                        db_session.add(req_user)
                        db_session.commit()
                    except:
                        db_session.rollback()
                        return ("DataBase Failed", 503, )
                    else:
                        return ("Have sent add request to {user}".format(user = resp_user.username), 200)
        else:
            return ("Please upload a json data", 403)

    def delete(self, name):
        if name is None:
            return ("The account name can't be None", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception,e:
                return ("The json data can't be parsed", 403, )
            db_session = get_session()
            db_session.begin()
            try:
                req_id = db_session.query(UserInfo.id).filter(and_(UserInfo.username == name,
                                    UserInfo.deleted == False)).first()
                if req_id is None:
                    db_session.rollback()
                    return ('Please create the user {name}'.format(name = name), 403)

                friend = db_session.query(FriendList).with_lockmode('update').filter(and_(FriendList.index == req_id[0],
                                    FriendList.username == para['account'])).first()
                if friend is not None:
                    db_session.delete(friend)
                db_session.commit()
            except Exception,e:
                db_session.rollback()
                return ("Delete friend {account} failed due to DataBase error".format(account = para['account']), 500)
            if para['bidirectional'] == True:
                db_session.begin()
                try:
                    resp_user = db_session.query(UserInfo).join(FriendList).with_lockmode('update').\
                                filter(and_(UserInfo.username == para['account'], FriendList.username == name)).first()
                    if (resp_user is not None) and len(resp_user.friends) != 0:
                        db_session.delete(resp_user.friends[0])
                    db_session.commit()
                except Exception,e:
                    db_session.rollback()
                    return ("Failed to delete your account in opposing friendlist", 500)
            return ('Delete successfully', 200)
        else:
            return ("Please upload a json data", 403)

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
                req_user = db_session.query(UserInfo).with_lockmode('read').filter(
                                and_(UserInfo.username == name, UserInfo.deleted == False,
                                     UserInfo.state != 'offline')).one()
            except Exception,e:
                return ("The account {account} is not exist or offline".format(account = name), 404)
            else:
                for user in req_user.friends:
                    if user.username == para['account']:
                        if user.confirmed:
                            return ('The account {account} is already your friend'.format(
                                        account = para['account']), 202)
                        else:
                            message = dict()
                            message['method'] = "add_friend_resp"
                            tmp = dict()
                            tmp['from'] = req_user.username
                            tmp['to'] = para['account']
                            db_session.begin()
                            if para['result'] == 'accept':
                                user.confirmed = True
                                tmp['msg'] = 'accept'
                                db_session.add(req_user)
                            else:
                                tmp['msg'] = 'reject'
                                db_session.delete(user)
                            try:
                                db_session.commit()
                            except:
                                db_session.rollback()
                                tmp['msg'] = 'failed'
                                message['para'] = tmp
                                send_message(req_user.username, para['account'], message)
                                return ("DataBase Failed", 503, )
                            else:
                                message['para'] = tmp
                                ret = send_message(req_user.username, para['account'], message)
                                if not ret:
                                    return ("You have processed the add request from {account}".format(
                                            account = para['account']), 200)
                                else:
                                    return ret
                try:
                    resp_user = db_session.query(UserInfo).join(FriendList).with_lockmode('read').filter(
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
                        req_user.friends.append(FriendList(para['account'], resp_user.nickname, resp_user.state, True))
                        tmp['msg'] = 'accept'
                    elif para['result'] == 'reject':
                        tmp['msg'] = 'reject'
                    else:
                        tmp['msg'] = 'failed'
                    db_session.begin()
                    try:
                        db_session.add(req_user)
                        db_session.commit()
                    except:
                        db_session.rollback()
                        tmp['msg'] = 'failed'
                        message['para'] = tmp
                        send_message(req_user.username, resp_user.username, message)
                        return ("DataBase Failed", 503, )
                    else:
                        message['para'] = tmp
                        ret = send_message(req_user.username, resp_user.username, message)
                        if not ret:
                            return ("You have processed the add request from {account}".format(
                                account = resp_user.username), 200)
                        else:
                            return ret
        else:
            return ("Please upload a json data", 403)


