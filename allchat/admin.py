# -*- coding: utf-8 -*-
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import BaseView, expose
from flask.ext.admin.contrib.fileadmin import FileAdmin
import os.path as op
from allchat import admin, db
from allchat.database.models import UserInfo, UserAuth, FriendList, GroupMember, GroupInfo
path = op.join(op.abspath(op.join(op.dirname(__file__), op.pardir)), 'static')


admin.add_view(ModelView(UserInfo, db.session, name="UserInfo"))
admin.add_view(ModelView(UserAuth, db.session, name="UserAuth"))
admin.add_view(ModelView(FriendList, db.session, name="FriendList"))
admin.add_view(ModelView(GroupInfo, db.session, name="GroupInfo"))
admin.add_view(ModelView(GroupMember, db.session, name="GroupMember"))
admin.add_view(FileAdmin(path, '/static/', name='Static Files'))
