from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupMember, FriendList
from sqlalchemy import and_
import time, string

class login_view(MethodView):
    def get(self):
        return make_response(("This is the login page", 200, ))
    def post(self,name):
        if("flush" in request.headers and request.headers['flush'] == "1"):
            if 'account' in request.cookies and 'account' in session \
                    and session['account'] == request.cookies['account']:
                db_session = get_session()
                try:
                    db_user = db_session.query(UserInfo).filter_by(username = name).one()
                except Exception, e:
                    return make_response(("The user is not registered yet", 403, ))
                db_session.begin()
                db_user.state = db_user.last_state if db_user.last_state != "offline" else "invisible"
                db_user.last_state = db_user.state
                tmp_state = db_user.state if db_user.state == "online" else "offline"
                db_groupmember = db_session.query(GroupMember).filter_by(member_account = name).all()
                for db_member in db_groupmember:
                    db_member.member_logstate = tmp_state
                db_friendlist = db_session.query(FriendList).filter_by(username = name).all()
                for db_friend in db_friendlist:
                    db_friend.state = tmp_state
                try:
                    db_session.commit()
                except:
                    db_session.rollback()
                    return ("DataBase Failed", 503, )
                else:
                    return make_response(("Flush successfully", 200, ))
            else:
                return make_response(("Failed to flush", 403, ))
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            logstate = para['state']
            if logstate == "offline":
                if 'account' in request.cookies and 'account' in session \
                        and session['account'] == request.cookies['account']:
                    db_session = get_session()
                    try:
                        db_user = db_session.query(UserInfo).filter_by(username = name).one()
                    except Exception, e:
                        return make_response(("The user is not registered yet", 403, ))
                    db_session.begin()
                    db_user.state = "offline"
                    db_groupmember = db_session.query(GroupMember).filter_by(member_account = name).all()
                    for db_member in db_groupmember:
                        db_member.member_logstate = "offline"
                    db_friendlist = db_session.query(FriendList).filter_by(username = name).all()
                    for db_friend in db_friendlist:
                        db_friend.state = "offline"
                    try:
                        db_session.commit()
                    except:
                        db_session.rollback()
                        return ("DataBase Failed", 503, )
                    else:
                        return make_response(("Logout successfully", 200, ))
                else:
                    return make_response(("Failed to logout", 403, ))
            password = para['password']
            if(logstate not in ['online', 'invisible']):
                return make_response(("The login state is illegal", 403, ))
            db_session = get_session()
            try:
                db_user = db_session.query(UserInfo).filter_by(username = name).one()
            except Exception, e:
                return make_response(("The user is not registered yet", 403, ))
            if(password == db_user.password):
                db_session.begin()
                db_user.state = logstate
                db_user.last_state = logstate
                db_user.login = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time()))
                tmp_state = db_user.state if db_user.state == "online" else "offline"
                db_groupmember = db_session.query(GroupMember).filter_by(member_account = name).all()
                for db_member in db_groupmember:
                    db_member.member_logstate = tmp_state
                db_friendlist = db_session.query(FriendList).filter_by(username = name).all()
                for db_friend in db_friendlist:
                    db_friend.state = tmp_state
                try:
                    db_session.commit()
                except:
                    db_session.rollback()
                    return ("DataBase Failed", 503, )
                #render_template to new page or stay at current page?
                session.permanent = False
                session['account'] = name
                resp = make_response(("Successful logged in", 200, ))
                resp.set_cookie("account", value=name)
                return resp
            else:
                return make_response(("Password is wrong, please check out", 403, ))
        else:
            return make_response(("Please upload a json data", 403, ))
