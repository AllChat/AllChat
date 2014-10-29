from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupMember, FriendList, GroupInfo, UserAuth
# from sqlalchemy import and_
from allchat import db
import time, string, base64, threading
from allchat.amqp.Impl_kombu import send_message

class login_view(MethodView):
    def get(self):
        return make_response(("This is the login page", 200, ))
    def post(self,name):
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            if 'state' not in para:
                return make_response("No status information", 403)
            logstate = para['state']
            if logstate == "offline":
                db_session = get_session()
                try:
                    auth = db_session.query(UserAuth).filter(db._and(UserAuth.account == name, \
                                                                    UserAuth.deleted == False)).one()
                except:
                    return make_response('Account error', 500)
                if name == session['account'] and auth.is_token(session['token']):
                    def callback(name):
                        db_session = get_session()
                        try:
                            db_user = db_session.query(UserInfo).filter(db.and_(UserInfo.username == name, \
                                                                                UserInfo.state != "offline")).one()
                            auth = db_session.query(UserAuth).filter(db.and_(UserAuth.account == name, \
                                                                    UserAuth.deleted == False)).one()
                        except Exception, e:
                            return None
                        db_session.begin()
                        db_user.state = "offline"
                        db_groupmember = db_session.query(GroupMember).filter_by(member_account = name).all()
                        for db_member in db_groupmember:
                            prev_state = "offline" if db_member.member_logstate != "online" else "online"
                            db_member.member_logstate = "offline"
                            if prev_state != "offline":
                                group_update_status(name, db_member.member_account, "offline")
                        db_friendlist = db_session.query(FriendList).filter_by(username = name).all()
                        for db_friend in db_friendlist:
                            prev_state = "offline" if db_friend.state != "online" else "online"
                            db_friend.state = "offline"
                            if db_friend.user.state != "offline" and prev_state != "offline":
                                friendlist_update_status(name, db_friend.user.username, "offline")
                        try:
                            auth.clear()
                            db_session.commit()
                        except:
                            db_session.rollback()
                        else:
                            pass
                    if name in login_timer:
                        try:
                            login_timer[name].cancel()
                        except:
                            pass
                        del login_timer[name]
                    login_timer[name] = threading.Timer(120.0, callback, args = [name])
                    login_timer[name].start()
                    return make_response("Succeed to logout", 200)
                else:
                    return make_response(("Failed to logout", 403, ))
            if 'password' not in para:
                return make_response(("No password", 403, ))
            password = para['password']
            if(logstate not in ['online', 'invisible']):
                return make_response(("The login state is illegal", 403, ))
            db_session = get_session()
            try:
                db_user = db_session.query(UserInfo).filter(db.and_(UserInfo.username == name, \
                                                                    UserInfo.deleted == False)).one()
                auth = db_session.query(UserAuth).filter(db.and_(UserAuth.account == name, \
                                                                    UserAuth.deleted == False)).one()
            except Exception, e:
                return make_response(("Account or password error", 403, ))
            if auth.is_authenticated(password):
                db_session.begin()
                db_user.last_state = db_user.state
                db_user.state = logstate
                db_user.login = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time()))
                tmp_state = db_user.state
                db_groupmember = db_session.query(GroupMember).filter_by(member_account = name).all()
                for db_member in db_groupmember:
                    prev_state = "offline" if db_member.member_logstate != "online" else "online"
                    now_state = "offline" if tmp_state != "online" else "online"
                    db_member.member_logstate = tmp_state
                    if prev_state != now_state:
                        group_update_status(name, db_member.group_id, now_state)
                db_friendlist = db_session.query(FriendList).filter_by(username = name).all()
                for db_friend in db_friendlist:
                    prev_state = "offline" if db_friend.state != "online" else "online"
                    now_state = "offline" if tmp_state != "online" else "online"
                    db_friend.state = tmp_state
                    if db_friend.user.state != "offline" and prev_state != now_state:
                        friendlist_update_status(name, db_friend.user.username, now_state)
                try:
                    auth.fresh()
                    db_session.commit()
                except:
                    db_session.rollback()
                    return ("DataBase Failed", 503, )
                #render_template to new page or stay at current page?
                session.permanent = False
                session['account'] = name
                session['token'] = auth.token
                resp = make_response(("Successful logged in", 200, ))
                # resp.set_cookie("account", value = name)
                # resp.set_cookie("nickname", value = base64.b64encode(db_user.nickname.encode("utf8")))
                # resp.set_cookie("icon", value = str(db_user.icon))
                resp.headers['account'] = name
                resp.headers['nickname'] = base64.b64encode(db_user.nickname.encode("utf8"))
                resp.headers['icon'] = str(db_user.icon)
                return resp
            else:
                return make_response(("Password is wrong, please check out", 403, ))
        else:
            return make_response(("Please upload a json data", 403, ))

login_timer = {}

def friendlist_update_status(sender, receiver, state):
    tmp = {}
    tmp['method'] = "friendlist_update_status"
    tmp['from'] = sender
    tmp['to'] = receiver
    tmp['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    tmp['msg'] = state
    message = {}
    message['para'] = tmp
    return send_message(sender, receiver, message)

def group_update_status(sender, group_id, state):
    db_session = get_session()
    try:
        group = db_session.query(GroupInfo).join(GroupMember).filter(db.and_(GroupInfo.group_id == group_id,
                GroupMember.member_account != sender, GroupMember.member_logstate != "offline")).one()
    except:
        return ("Failed to change group {0}'s state".format(group_id), 403)
    tmp = {}
    tmp['method'] = "friendlist_update_status"
    tmp['from'] = sender
    tmp['to'] = None
    tmp['group_id'] = group_id
    tmp['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    tmp['msg'] = state
    message = {}
    message['para'] = tmp
    for user in group.groupmembers:
        message['para']['to'] = user.member_account
        send_message(sender, user.member_account, message)
    return None