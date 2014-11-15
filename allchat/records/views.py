from flask.views import MethodView
from flask import request, make_response, g, session, jsonify
from allchat.database.sql import get_session
from allchat.database.models import UserInfo, GroupMember, FriendList, GroupInfo
# from sqlalchemy import and_
from allchat import db
from allchat.authentication import authorized
from allchat.filestore.retrieve import getMessages
from allchat.path import get_single_msg_dir,get_group_msg_dir

class records_view(MethodView):
    @authorized
    def get(self):
        user_name = session.get("account")
        header = request.headers
        type_ = header.get("type")
        identity = header.get("identity")
        start_date = header.get("start_date")
        end_date = header.get("end_date")
        if not all(type_,identity,start_date,end_date):
            return make_response(("Missing critical information.", 403))

        db_session = get_session()

        if type_ == 'group':
            try:
                db_user = db_session.query(GroupMember).filter(db.and_(GroupMember.group_id == identity, GroupMember.member_account == user_name)).one()
            except:
                return make_response(('User not in the group!',404))
            directory = os.path.join(get_group_msg_dir(),str(identity))
        elif type_ == 'user':
            try:
                ##search database if the friend relationship exist
                db_user = db_session.query(UserInfo).join(FriendList).filter(db.and_(UserInfo.username == user_name, FriendList.username == identity, FriendList.confirmed == True )).one()
            except:
                return make_response(('Requested users are not friends.',404))
            directory = os.path.join(get_single_msg_dir(),"&&".join((user_name,identity)))
        else:
            return make_response(('Chattype wrong.',403))

        chat_record = getMessages(directory,start_date,end_date)
        return jsonify(chat_record)
