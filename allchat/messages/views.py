# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import request, make_response, session, escape, jsonify
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, FriendList, GroupInfo, GroupMember
from allchat.amqp.Impl_kombu import send_message, receive_message
# from sqlalchemy import and_, or_
from allchat import db
import time, base64, os
from allchat.filestore import saver
from allchat.authentication import authorized, checked
from allchat.path import get_picture_dir


class messages_view(MethodView):
    @authorized
    def get(self, type, user, file):
        if not ('account' in session and session['account'] == user):
            return make_response("Please login first", 404)
        if type == 'text':
            db_session = get_session()
            try:
                account = db_session.query(UserInfo).filter(db.and_(UserInfo.deleted == False,
                                UserInfo.state != 'offline', UserInfo.username == user)).one()
            except Exception as e:
                return ("Account {0} doesn't exist or logout now".format(user), 404)
            if not file:
                msg = receive_message(account.username)
                if msg:
                    return jsonify(msg)
                else:
                    return ("Time out", 404)
            else:
                return ("URL error", 403)
        elif type == 'image':
            db_session = get_session()
            try:
                account = db_session.query(UserInfo).filter(db.and_(UserInfo.deleted == False,
                                UserInfo.state != 'offline', UserInfo.username == user)).one()
            except Exception as e:
                return ("Account {0} doesn't exist or logout now".format(user), 404)
            if file:
                name, tag = os.path.splitext(file)
                if tag is None:
                    return ('file extension is not allowed', 403)
                path = os.path.join(get_picture_dir(),file)
                tmp = dict()
                tmp['type'] = tag.lstrip('.')
                try:
                    with open(path, "rb") as fp:
                        tmp['content'] = base64.b64encode(fp.read())
                except IOError:
                    return ('Not found', 404)
                except Exception as e:
                    return ('Operation Failed', 500)
                return jsonify(tmp)
            else:
                return ('Not found', 404)
        elif type == 'sound':
            pass
        elif type == 'video':
            pass
        else:
            return ('Type {0} is not found'.format(type), 404)

    @authorized
    def post(self, type):
        content_type = request.environ['CONTENT_TYPE'].split(';', 1)[0]
        tmp = content_type.split(';', 1)[0]
        if tmp == "application/json":
            try:
                if type == "individual":
                    return self.individual_message()
                elif type == "group":
                    return self.group_message()
                else:
                    return ("Error URL", 403)
            except Exception as e:
                return ("Failed to pass the message", 500)
        else:
            return ("Error Content_Type in the request, please upload a "
                    "application/json request", 403)

    def individual_message(self):
        try:
            para = request.get_json()
        except Exception as e:
            return ("The json data can't be parsed", 403, )
        try:
            sender = request.headers['message_sender']
            receiver = request.headers['message_receiver']
        except Exception as e:
            return ("HTTP header format error", 403)
        if sender != session['account']:
            return ("Account error", 403)
        users = []
        db_session = get_session()
        users.extend(db_session.query(UserInfo).join(FriendList).filter(UserInfo.username == sender)
                     .filter(db.and_(UserInfo.state != "offline", UserInfo.deleted == False)).all())
        users.extend(db_session.query(UserInfo).join(FriendList)
                    .filter(db.and_(UserInfo.username == receiver, UserInfo.deleted == False)).all())
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
                break
        if not flag:
            return ('Forbidden! The recipient is not your friend.', 403)

        message = dict()
        message['method'] = "send_individual_message"
        tmp = dict()
        tmp['from'] = user_from.username
        tmp['to'] = user_to.username
        tmp['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        record = ""
        for pic in para['msg']:
            if(pic['type'] == "text"):
                record += escape(pic['content'])
                continue
            elif(pic['type'] in ['jpg', 'png', 'bmp', 'gif', 'psd', 'jpeg']):
                path = saver.savePicture(base64.b64decode(pic['content']), pic['type'])
                pic_name = path.split('\\')[-1]
                pic['content'] = pic_name
                record += "@$^*" + path + "@$^*"
        tmp['msg'] = para['msg']
        message['para'] = tmp
        ret = None
        for i in range(0,3):
            ret = send_message(user_from.username, user_to.username, message)
            if not ret:
                saver.saveSingleMsg(user_from.username, user_to.username,
                                        [tmp['time'], record])
                return ("Send message successfully", 200)
            else:
                continue
        return ret


    def group_message(self):
        try:
            para = request.get_json()
        except Exception as e:
            return ("The json data can't be parsed", 403, )
        sender = request.headers['message_sender']
        group_id = int(request.headers['group_id'])
        if sender != session['account']:
            return ("Account error", 403)
        db_session = get_session()
        try:
            user_from = db_session.query(UserInfo).filter(UserInfo.username == sender).\
                                filter(db.and_(UserInfo.state != "offline",
                                UserInfo.deleted == False)).one()
        except Exception as e:
            return ('Message send failed due to the sender not exist or offline', 403)
        try:
            group_to = db_session.query(GroupInfo).join(GroupMember).filter(
                                    GroupInfo.group_id == group_id).one()
        except Exception as e:
            return ("Group doesn't exist", 403)
        message = dict()
        message['method'] = 'send_group_message'
        tmp = dict()
        tmp['from'] = user_from.username
        tmp['to'] = None
        tmp['group_id'] = group_id
        tmp['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        record = ""
        for pic in para['msg']:
            if(pic['type'] == "text"):
                record += escape(pic['content'])
                continue
            elif(pic['type'] in ['jpg', 'png', 'bmp', 'gif', 'psd', 'jpeg']):
                path = saver.savePicture(base64.b64decode(pic['content']), pic['type'])
                pic_name = path.split('\\')[-1]
                pic['content'] = pic_name
                record += "@$^*" + path + "@$^*"
        tmp['msg'] = para['msg']
        message['para'] = tmp
        saver.saveGroupMsg(sender, group_to.group_id,[tmp['time'], record])
        failed = []
        for user in group_to.groupmembers:
            if user.member_account == user_from.username or user.confirmed == False:
                continue
            message['para']['to'] = user.member_account
            ret = send_message(user_from.username, user.member_account, message)
            if ret:
                failed.append(user.member_account)
        last = []
        for user in failed:
            ret = None
            for i in range(0, 2):
                message['para']['to'] = user
                ret = send_message(user_from.username, user, message)
                if not ret:
                    break
            if ret:
                last.append(user)
        if len(last) != 0:
            return ('Message send partly failed', 206)
        return ("Send message successfully", 200)



