# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import request, make_response, g, session, jsonify, json
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupMember, FriendList, GroupInfo
# from sqlalchemy import and_, desc
from allchat import db
from allchat.amqp.Impl_kombu import RPC, cast, send_message
from allchat.authentication import authorized
import datetime


class groups_view(MethodView):
    @authorized
    def get(self):
        header = request.headers
        if 'group_id' in header and 'account' in header:
            group_id = int(header['group_id'])
            account = header['account']
            db_session = get_session()
            try:
                db_user = db_session.query(UserInfo).filter_by(username = account).one()
            except:
                return ("Invalid user.", 404)
            # return all the groups the user has joined, including group_id and group_name
            if group_id == 0:
                try:
                    groups = db_session.query(GroupMember).filter(db.and_(GroupMember.member_account == account,
                        GroupMember.confirmed == True)).all()
                except:
                    return ("DataBase Failed querying groups info", 503 )
                group_list = dict()
                for group in groups:
                    group_list[group.group_id] = dict([("name",group.group_name),("role",group.role)])
                return (jsonify(group_list), 201)
            # return the member information of the specified group, check if the user is member or not
            else:
                try:
                    group = db_session.query(GroupInfo).join(GroupMember).filter(GroupInfo.group_id == group_id).one()
                except:
                    return ("Group "+group_id+" not found.", 404)
                if account not in [member.member_account for member in group.groupmembers if member.confirmed==True]:
                    return ("You are not in this group, access denied.", 405)
                member_list = dict()
                for member in group.groupmembers:
                    if member.confirmed:
                        tmp = dict()
                        tmp['nickname'] = member.nickname
                        tmp['state'] = member.member_logstate
                        tmp['icon'] = member.icon
                        tmp['role'] = member.role
                        member_list[member.member_account] = tmp
                return (jsonify(member_list), 201)
        else:
            return ("Missing critical information.", 403)
        

    @authorized
    def post(self,method):
        if method is None:
            if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
                try:
                    para = request.get_json()
                except Exception as e:
                    resp = make_response(("The json data can't be parsed", 403, ))
                    return resp
                # parse the json data and handle the request
                account = para['account']
                group_name = para['group_name']
                userlist = []
                if 'userlist' in para:
                    userlist = para['userlist']
                # allocate group id auto increment by 1, start from 10000
                db_session = get_session()
                try:
                    db_user = db_session.query(UserInfo).filter_by(username = account).one()
                except Exception as  e:
                    return ("User not found", 404)
                max_group_id = db_session.query(GroupInfo.group_id).order_by(db.desc(GroupInfo.group_id)).first()
                if max_group_id is None:
                    group_id = 10000
                else:
                    group_id = max_group_id[0]+1
                # add users in userlist to group if userlist is not empty
                # update both GroupMember and GroupInfo 
                members = []
                member = GroupMember(group_id, group_name, account, db_user.state, db_user.nickname, db_user.icon, "owner", True)
                members.append(member)
                illegal_users = set()
                if userlist:
                    for user in {}.fromkeys(userlist).keys(): # eliminate the duplicated account
                        try:
                            db_user = db_session.query(UserInfo).filter_by(username = user).one()
                        except Exception as  e:
                            illegal_users.add(user)
                        else:
                            if user != account:
                                member = GroupMember(group_id, group_name, user, db_user.state, db_user.nickname, db_user.icon)
                                members.append(member)
                group = GroupInfo(group_id, account, group_name,len(members))
                db_session.begin()
                for member in members:
                    group.groupmembers.append(member)
                db_session.add(group)
                try:
                    db_session.commit()
                except:
                    db_session.rollback()
                    return ("DataBase Failed", 503, )
                if illegal_users:
                    return ("Group created,but these users are illegal:"+','.join(illegal_users), 202)
                else:
                    return ("Group created successfully!", 201)
            else:
                return ("Please upload a json data", 403)
        elif method == 'search':
            ## dongzai updated in 2014-07-26, revised in 2014-07-27
            # def searchGroup(self):
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
            response_chunk_size = 5
            if 'keyword' in para and 'account' in para and 'type' in para:
                keyword = para['keyword']
                account = para['account']
                search_type = para['type']
                db_session = get_session()
                try:
                    db_user = db_session.query(UserInfo).filter_by(username = account).one()
                except:
                    return ("Invalid user.", 404)
                if search_type == 'uncertain':
                    try:
                        offsets = int(para['offset'])*response_chunk_size
                    except:
                        offsets = 0
                    if not offsets:
                        try:
                            result_size = db_session.query(GroupInfo).filter(GroupInfo.group_name.like\
                                ('%'+keyword+'%')).count()
                        except:
                            return ("Database Error.", 500)
                    try:
                        groups = db_session.query(GroupInfo).filter(GroupInfo.group_name.like\
                            ('%'+keyword+'%')).offset(offsets).limit(response_chunk_size).all()
                    except:
                        return ("Database Error.", 500)
                elif search_type == 'certain':
                    try:
                        groups = db_session.query(GroupInfo).filter_by(group_name = keyword).one()
                    except:
                        return ("Group not found.", 404)
                else:
                    return ("Search type unsupported.", 403)
                group_info = dict()
                if hasattr(groups,'__iter__'):
                    result = groups
                    if not offsets:
                        group_info['result_size'] = result_size
                        group_info['chunk_size'] = response_chunk_size
                else:
                    result = [groups]
                    group_info['result_size'] = len(result)
                group_info['groups'] = list()
                for group in result:
                    temp = dict()
                    temp['group_name'] = group.group_name
                    temp['group_id'] = group.group_id
                    temp['group_owner'] = group.owner
                    temp['group_size'] = group.group_size
                    group_info['groups'].append(temp)
                return jsonify(group_info)
            else:
                return ("Missing critical information.", 403)
        else:
            return ("Incorrect method.", 501)

    @authorized
    def put(self,groupID):
        if groupID is None:
            return ("Error in the URL. Please contain proper group id in the URL.", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            # check the account and operation, whether match or not
            # if match then proceed, if not return wrong information
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            account = para.get('account')
            operation = para.get('operation')
            db_session = get_session()
            try:
                db_user = db_session.query(UserInfo).filter_by(username = account).one()
            except Exception as  e:
                return ("Invalid user.", 404)
            try:
                db_group = db_session.query(GroupInfo).filter_by(group_id = groupID).one()
            except Exception as  e:
                return ("Group not found", 404)
            # this is the group owner try to add or del group member
            if session['account'] == db_group.owner:
                if operation == "add":
                    for member in db_group.groupmembers:
                        if member.member_account == account:
                            if member.confirmed == False:
                                message = dict()
                                message['method'] = 'join_group_confirm'
                                tmp = dict()
                                tmp['groupid'] = groupID
                                tmp['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                db_session.begin()
                                member.confirmed = True
                                db_group.group_size += 1
                                db_session.add(db_group)
                                try:
                                    db_session.commit()
                                except:
                                    db_session.rollback()
                                    tmp['result'] = 'failed'
                                    message['para'] = tmp
                                    send_message(db_group.owner,member.member_account,message)
                                    return ("DataBase Failed", 503)
                                tmp['result'] = 'success'
                                message['para'] = tmp
                                send_message(db_group.owner,member.member_account,message)
                            else:
                                return ("User %s already in group."%(account), 201)
                            break
                    else:
                        db_session.begin()
                        db_group.groupmembers.append(GroupMember(groupID, db_group.group_name, account, 
                                            db_user.state,db_user.nickname, db_user.icon,"member",True))
                        db_group.group_size += 1
                        db_session.add(db_group)
                        try:
                            db_session.commit()
                        except:
                            db_session.rollback()
                            return ("DataBase Failed", 503 )
                    return ("Users added to the group successfully.", 201)
                elif operation == "del":
                    if account == db_group.owner:
                        return ("The group owner can't be deleted.", 405)
                    for member in db_group.groupmembers:
                        if member.member_account == account:
                            if member.confirmed == False:
                                message = dict()
                                message['method'] = 'join_group_confirm'
                                tmp = dict()
                                tmp['groupid'] = groupID
                                tmp['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                tmp['result'] = 'rejected'
                                message['para'] = tmp
                                send_message(db_group.owner,member.member_account,message)
                            else:
                                db_group.group_size -= 1
                            db_session.begin()
                            db_group.groupmembers.remove(member)
                            db_session.add(db_group)
                            try:
                                db_session.commit()
                            except:
                                db_session.rollback()
                                return ("DataBase Failed", 503, )
                            break
                    else:
                        return ("Users to be deleted does not exist.", 404)
                    return ("Users deleted from the group successfully", 201)                        
                else:
                    return ("Operation not supported", 405)

            # this is a member trying to quit or a non-member trying to join in
            else:
                if operation not in ["join","quit"]:
                    return ("Operation not supported", 405)
                else:
                    if operation == "join":
                        # send group owner an applying msg, when the owner confirms, send the applicant a msg
                        try:
                            db_member = db_session.query(GroupMember).filter(db.and_(GroupMember.group_id==groupID,
                                GroupMember.member_account==account)).one()
                        except:
                            message = dict()
                            message['method'] = "join_group_apply"
                            tmp = dict()
                            tmp['applicant'] = account
                            tmp['groupid'] = groupID
                            tmp['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            tmp['msg'] = para.get("message","")
                            message['para'] = tmp
                            cnn = RPC.create_connection()
                            sender = RPC.create_producer(account, cnn)
                            try:
                                cast(sender, json.dumps(message), db_group.owner)
                            except:
                                RPC.release_producer(account)
                                RPC.release_connection(cnn)
                                return ("Applying failed due to system error", 500)
                            RPC.release_producer(account)
                            RPC.release_connection(cnn)
                            member = GroupMember(groupID,db_group.group_name,account,db_user.state,db_user.nickname, db_user.icon)
                            db_group.groupmembers.append(member)
                            db_session.begin()
                            try:
                                db_session.add(db_group)
                                db_session.commit()
                            except:
                                db_session.rollback()
                                return ("DataBase Failed", 503, )
                            return ("Application has been dealt, please wait for the owner to handle.", 201)
                        else:
                            if db_member.confirmed:
                                return ("You are already in the group", 400)
                            else:
                                return ("Please do not send duplicate requests.", 400)
                    if operation == "quit":
                        #validate user identity and proceed depend on the result
                        existed_members = [member.member_account for member in db_group.groupmembers]
                        if account in existed_members:
                            applicant = ''
                            for member in db_group.groupmembers:
                                if member.member_account == account:
                                    applicant = member
                                    break
                            db_session.begin()
                            db_group.groupmembers.remove(applicant)
                            db_group.group_size -= 1
                            db_session.add(db_group)
                            try:
                                db_session.commit()
                            except:
                                db_session.rollback()
                                return ("DataBase Failed", 503, )
                            return ("Quit the group successfully.", 201)
                        else:
                            return ("You are not a member of this group.", 405)
        else:
            return ("Please upload a json data", 403)

    @authorized
    def delete(self, groupID):
        if groupID is None:
            return ("Error in the URL. Please contain proper group id in the URL.", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            # check whether the applying user is the owner of the group
            try:
                para = request.get_json()
            except Exception as e:
                resp = make_response(("The json data can't be parsed", 403, ))
                return resp
            account = para['account']
            db_session = get_session()
            try:
                db_group = db_session.query(GroupInfo).filter_by(group_id = groupID).one()
            except Exception as  e:
                return ("Group not found", 404)
            if account != db_group.owner:
                return ("You don't have the permission to the operation", 405)
            # permission validated, delete the group info from GroupInfo and GroupMember
            db_session.begin()
            db_session.delete(db_group)
            try:
                db_session.commit()
            except:
                db_session.rollback()
                return ("DataBase Failed", 503, )
            return ("Group deleted successfully", 201)
        else:
            return ("Please upload a json data", 403)
