# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import request, make_response, session, jsonify, Response
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, UserAuth,GroupMember, FriendList
from sqlalchemy import and_
from allchat.amqp.Impl_kombu import RPC
from allchat.messages.handles import rpc_callbacks
from allchat.login.views import friendlist_update_status, group_update_status
from allchat.authentication import authorized
import re

tmp_str = "^[\w!@#$%^&*_.]+$"

class accounts_view(MethodView):
    def post(self):
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
                
            account = para['account']
            password = para['password']
            nickname = para['nickname']
            email = para['email']
            if not all((account, password, nickname, email)):
                return make_response(("Missing important data in the request", 400, ))
            tmp_re = re.compile(tmp_str)
            if (len(account) > 50) or not tmp_re.match(account):
                return make_response(("The account {0} is illegal".format(account), 400, ))
            if (len(password) > 50) or not tmp_re.match(password):
                return make_response(("The password {0} is illegal".format(password), 400, ))
            if len(nickname) > 50:
                return make_response(("The nickname {0} exceed the maximum length".format(nickname), 400, ))
            if (len(email) > 100) or (len(email.split('@')) != 2):
                return make_response(("The email {0} is unacceptable".format(nickname), 400, ))
            db_session = get_session()
            try:
                db_user = db_session.query(UserInfo).filter_by(username = account).one()
            except Exception, e:
                user = UserInfo(account, email, nickname)
                auth = UserAuth(account, password)
                db_session.begin()
                try:
                    db_session.add(user)
                    db_session.add(auth)
                    db_session.commit()
                except:
                    db_session.rollback()
                    return ("DataBase Failed", 503, )
                tmp = rpc_callbacks()
                RPC.register_callbacks(user.username, [tmp])
                queue = RPC.create_queue(user.username, user.username)
                cnn = RPC.create_connection()
                RPC.create_consumer(user.username, cnn, queue)
                RPC.release_consumer(user.username)
                RPC.release_connection(cnn)
                resp = Response("Account is created successfully", 201, )
                return resp
            else:
                if not db_user.deleted:
                    return make_response(("The account {0} is already existed".format(account), 400, ))
                else:
                    auth = db_session.query(UserAuth).filter(UserAuth.account == db_user.username).first()
                    if len(auth) < 1:
                        return make_response(("The account {0} is already existed".format(account), 400, ))
                    if auth.is_authenticated(password):
                        db_session.begin()
                        try:
                            auth.activate()
                            db_user.deleted = False
                            db_session.add(db_user)
                            db_session.commit()
                        except:
                            db_session.rollback()
                            return ("DataBase Failed", 503, )
                        RPC.create_queue(db_user.username, db_user.username)
                        resp = Response("Account is recoveried successfully", 200, {'token':auth.token})
                        return resp
                    else:
                        return make_response(("The account {0} is already existed".format(account), 400, ))
        else:
            return make_response(("Please upload a json data", 403, ))
    @authorized
    def put(self, name):
        if( name is None):
            return ("Account name shouldn't be None", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            old_password = None
            new_password = None
            nickname = None
            email = None
            icon = None
            state = None
            if(('new_password' in para) and ('old_password' in para)):
                old_password = para['old_password']
                new_password = para['new_password']
            if('nickname' in para):
                nickname = para['nickname']
            if('email' in para):
                email = para['email']
            if('icon' in para):
                icon = int(para['icon'])
            if('state' in para):
                state = para['state']
            if(not any((old_password, new_password, nickname, email, icon, state))):
                return ("No content in request", 202)
            db_session = get_session()
            try:
                user = db_session.query(UserInfo).filter(and_(UserInfo.username == name, UserInfo.deleted == False)).one()
                auth = db_session.query(UserAuth).filter(and_(UserAuth.account == name, UserInfo.deleted == False)).one()
            except Exception, e:
                return make_response(("The account {0} isn't existed".format(name), 404, ))
            if all((new_password, old_password)):
                tmp_re = re.compile(tmp_str)
                if not auth.is_authenticated(old_password) or tmp_re.match(new_password):
                    return ("Account or Password is not corrected", 403, )
            if(nickname):
                if(user.state != 'offline'):
                    if(len(nickname) > 50 ):
                        return make_response(("The nickname {0} exceed the maximum length".format(nickname), 400, ))
                    else:
                        user.nickname = nickname
                else:
                    return ("Please login first", 401, )
            if(email):
                if(user.state != 'offline'):
                    if(len(email) > 100 or (len(email.split('@')) != 2)):
                        return make_response(("The email {0} is unacceptable".format(email), 400, ))
                    else:
                        user.email = email
                else:
                    return ("Please login first", 401, )
            if(icon):
                if(user.state != 'offline'):
                    if(icon > 255 or icon < 0):
                        return make_response(("The icon number {0} is unacceptable".format(icon), 400, ))
                    else:
                        user.icon = icon
                else:
                    return ("Please login first", 401, )
            if(state and state in ("online", "offline", "invisible") and state != user.state):
                if user.state == "offline":
                    return ("Please login first", 401, )
                else:
                    user.last_state = user.state
                    user.state = state
            db_session.begin()
            if any([icon, state, nickname]):
                db_groupmember = db_session.query(GroupMember).filter_by(member_account = name).all()
                for db_member in db_groupmember:
                    prev_state = "offline" if db_member.member_logstate != "online" else "online"
                    now_state = "offline" if user.state != "online" else "online"
                    db_member.member_logstate = user.state
                    db_session.add(db_member)
                    if prev_state != now_state:
                        group_update_status(name, db_member.member_account, now_state)
                db_friendlist = db_session.query(FriendList).filter_by(username = name).all()
                for db_friend in db_friendlist:
                    prev_state = "offline" if db_friend.state != "online" else "online"
                    now_state = "offline" if user.state != "online" else "online"
                    db_friend.state = user.state
                    db_friend.icon = user.icon
                    db_friend.nickname = user.nickname
                    db_session.add(db_friend)
                    if db_friend.user.state != "offline" and prev_state != now_state:
                        friendlist_update_status(name, db_friend.user.username, now_state)
            try:
                if all((new_password, old_password)):
                    auth.modify(old_password, new_password)
                db_session.add(user)
                db_session.commit()
            except:
                db_session.rollback()
                return ("DataBase Failed", 503, )
            if all((new_password, old_password)):
                resp = Response("The account is modified sucessfully", 200, {'token':auth.token})
                return resp
            else:
                return ("The account is modified sucessfully", 200, )
        else:
            return make_response(("Please upload a json data", 403, ))
    @authorized
    def delete(self, name):
        if( name is None):
            return ("Account name shouldn't be None", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json" and name is not None):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            if(not para['password']):
                return ('Please upload the account {user} password'.format(user = name), 401)
            db_session = get_session()
            try:
                user = db_session.query(UserInfo).filter(and_(UserInfo.username == name, UserInfo.deleted == False)).one()
                auth = db_session.query(UserAuth).filter(and_(UserAuth.account == name, UserInfo.deleted == False)).one()
            except Exception, e:
                return make_response(("The account {0} isn't existed or password is wrong".format(name), 404, ))
            if not auth.is_authenticated(para['password']):
                return ('Account or password is not corrected', 401)
            db_session.begin()
            try:
                auth.delete()
                user.deleted = True
                db_session.add(user)
                db_session.commit()
            except:
                db_session.rollback()
                return ("DataBase Failed", 503, )
            RPC.del_queue(user.username)
            return ("The account is deleted sucessfully", 200, )
        else:
            return make_response(("Please upload a json data", 403, ))
    @authorized
    def get(self, name):
        if name is None:
            return make_response(("Not developed.Try again later", 204))
        if 'mysql_like' in request.args and request.args['mysql_like'] == '1':
            if 'account' in request.cookies and 'account' in session \
                    and session['account'] == request.cookies['account']:
                db_session = get_session()
                try:
                    users = db_session.query(UserInfo).filter(and_(UserInfo.username.like("%" + name + "%"),
                            UserInfo.deleted != True)).all()
                except:
                    return ("Database Error", 500)
                msg = dict()
                msg['accounts'] = list()
                for user in users:
                    tmp = dict()
                    tmp['account'] = user.username
                    tmp['nickname'] = user.nickname
                    tmp['state'] = "offline" if user.state != "online" else "online"
                    tmp['icon'] = user.icon
                    msg['accounts'].append(tmp)
                return jsonify(msg)
            else:
                return ("Please login first", 403)
        else:
            #正常查询
            if 'account' in request.cookies and 'account' in session \
                    and session['account'] == request.cookies['account']:
                db_session = get_session()
                try:
                    user = db_session.query(UserInfo).filter(and_(UserInfo.username == name, UserInfo.deleted == False)).one()
                except:
                    msg = dict()
                    msg['accounts'] = list()
                    return jsonify(msg)
                msg = dict()
                msg['accounts'] = list()
                tmp = dict()
                tmp['account'] = user.username
                tmp['nickname'] = user.nickname
                tmp['state'] = "offline" if user.state != "online" else "online"
                tmp['icon'] = user.icon
                msg['accounts'].append(tmp)
                return jsonify(msg)
            else:
                return ("Please login first", 403)



