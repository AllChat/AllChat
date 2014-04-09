from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupList, FriendList, GroupInfo
import datetime, string, re

tmp_str = "^[\w@#$%^&*_.]+$"

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
            tmp_re = re.compile(tmp_str)
            if((len(account) > 50) or not (tmp_re.match(account))):
                return make_response(("The account {0} is illegal".format(account), 400, ))
            if((len(password) > 50) or not (tmp_re.match(password))):
                return make_response(("The password {0} is illegal".format(password), 400, ))
            if(len(nickname) > 50):
                return make_response(("The nickname {0} exceed the maximum length".format(nickname), 400, ))
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
                    return make_response(("The account {0} is already existed".format(account), 400, ))
                else:
                    if(password == db_user.password):
                        db_user.deleted = False
                        db_session.add(db_user)
                        db_session.commit()
                        return "Account is recoveried successfully"
                    else:
                        return make_response(("The account {0} is already existed".format(account), 400, ))
        else:
            return make_response(("Please upload a json data", 403, ))
    def put(self, name):
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            pass
    def delete(self, name):
        pass
    def get(self, name):
        pass
