from flask.views import MethodView
from flask import request, make_response, g, session
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupMember, FriendList, GroupInfo
from sqlalchemy import and_, desc
from allchat.amqp.Impl_kombu import RPC, cast


class groups_view(MethodView):
    def get(self):
        pass
    def post(self):
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
            except Exception, e:
                return ("User not found", 404)
            max_group_id = db_session.query(GroupInfo.group_id).order_by(desc(GroupInfo.group_id)).first()
            if max_group_id is None:
                group_id = 10000
            else:
                group_id = max_group_id[0]+1
            # add users in userlist to group if userlist is not empty
            # update both GroupMember and GroupInfo 
            user_count = 1
            member = GroupMember(group_id, account, db_user.state, "owner")
            db_session.add(member)
            illegal_users = set()
            if userlist:
                for user in {}.fromkeys(userlist).keys(): # eliminate the duplicated account
                    try:
                        db_user = db_session.query(UserInfo).filter_by(username = user).one()
                    except Exception, e:
                        illegal_users.add(user)
                    else:
                        if user != account:
                            member = GroupMember(group_id, user, db_user.state)
                            db_session.add(member)
                            user_count += 1
            group = GroupInfo(group_id, account, group_name,user_count)
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

    def put(self,groupID):
        if groupID is None:
            return ("Error in the URL. Please contain proper group id in the URL.", 403)
        if (request.environ['CONTENT_TYPE'].split(';', 1)[0] == "application/json"):
            pass
        else:
            return ("Please upload a json data", 403)

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
            except Exception, e:
                return ("Group not found", 404)
            if account != db_group.owner:
                return ("You don't have the permission to the operation", 405)
            # permission validated, delete the group info from GroupInfo and GroupMember 
            group_name = db_group.group_name
            db_session.delete(db_group)
            db_groupmember = db_session.query(GroupMember).filter_by(group_id = groupID).all()
            for db_member in db_groupmember:
                db_session.delete(db_member)
            try:
                db_session.commit()
            except:
                db_session.rollback()
                return ("DataBase Failed", 503, )
            return ("Group deleted successfully", 201)
        else:
            return ("Please upload a json data", 403)
