from flask.views import MethodView
from flask import request, make_response
from allchat.database.sql import get_session
from allchat.database.models import UserInfo
from sqlalchemy import and_
from allchat.amqp.Impl_kombu import RPC
from allchat.messages.handles import rpc_callbacks
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
            if(not all((account, password, nickname, email))):
                return make_response(("Missing important data in the request", 400, ))
            tmp_re = re.compile(tmp_str)
            if((len(account) > 50) or not (tmp_re.match(account))):
                return make_response(("The account {0} is illegal".format(account), 400, ))
            if((len(password) > 50) or not (tmp_re.match(password))):
                return make_response(("The password {0} is illegal".format(password), 400, ))
            if(len(nickname) > 50):
                return make_response(("The nickname {0} exceed the maximum length".format(nickname), 400, ))
            if((len(email) > 100) or (len(email.split('@')) != 2)):
                return make_response(("The email {0} is unacceptable".format(nickname), 400, ))
            db_session = get_session()
            try:
                db_user = db_session.query(UserInfo).filter_by(username = account).one()
            except Exception, e:
                user = UserInfo(account, password, email, nickname)
                db_session.add(user)
                try:
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
                return ("Account is created successfully", 201, )
            else:
                if(not db_user.deleted):
                    return make_response(("The account {0} is already existed".format(account), 400, ))
                else:
                    if(password == db_user.password):
                        try:
                            db_user.deleted = False
                            db_session.add(db_user)
                            db_session.commit()
                        except:
                            db_session.rollback()
                            return ("DataBase Failed", 503, )
                        RPC.create_queue(db_user.username, db_user.username)
                        return ("Account is recoveried successfully", 200, )
                    else:
                        return make_response(("The account {0} is already existed".format(account), 400, ))
        else:
            return make_response(("Please upload a json data", 403, ))
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
            if(('new_password' in para) and ('old_password' in para)):
                old_password = para['old_password']
                new_password = para['new_password']
            if('nickname' in para):
                nickname = para['nickname']
            if('email' in para):
                email = para['email']
            if(not any((old_password, new_password, nickname, email))):
                return ("No content in request", 202)
            db_session = get_session()
            try:
                user = db_session.query(UserInfo).filter(and_(UserInfo.username == name, UserInfo.deleted == False)).one()
            except Exception, e:
                return make_response(("The account {0} isn't existed".format(name), 404, ))
            if(all((new_password, old_password))):
                tmp_re = re.compile(tmp_str)
                if((user.password == old_password) and tmp_re.match(new_password)):
                    user.password = new_password
                else:
                    return ("Wrong Password", 403, )
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
            try:
                db_session.add(user)
                db_session.commit()
            except:
                db_session.rollback()
                return ("DataBase Failed", 503, )
            return ("The account is modified sucessfully", 200, )
        else:
            return make_response(("Please upload a json data", 403, ))
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
                user = db_session.query(UserInfo).filter(and_(UserInfo.username == name, UserInfo.deleted == False, UserInfo.password == para['password'])).one()
            except Exception, e:
                return make_response(("The account {0} isn't existed or password is wrong".format(name), 404, ))
            try:
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
    def get(self, name):
        pass
