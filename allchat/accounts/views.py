from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupList, FriendList, GroupInfo
import datetime

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
            if((len(account) > 50) or (len(password) > 50) or (len(nickname) > 50)):
                return make_response(("The user data exceed the maximum length", 400, ))
            db_session = get_session()
            try:
                db_user = db_session.query(UserInfo).filter_by(username = account).one()
            except Exception, e:
                user = UserInfo(account, password, nickname)
                db_session.add(user)
                db_session.commit()
                return "Account is created successfully"
            else:
                if(not db_user.deleted):
                    return make_response(("The account %s is already existed"%(account, ), 400, ))
                else:
                    if(password == db_user.password):
                        db_user.deleted = False
                        db_session.add(db_user)
                        db_session.commit()
                        return "Account is recoveried successfully"
                    else:
                        return make_response(("The account %s is already existed"%(account, ), 400, ))
        else:
            return make_response(("Please upload a json data", 403, ))
    def put(self, name):
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            pass
    def delete(self, name):
        pass
    def get(self, name):
        pass
