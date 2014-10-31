# -*- coding: utf-8 -*-
from flask import session, url_for, redirect, request
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import BaseView, expose, AdminIndexView, helpers
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin import Admin
from wtforms import form, fields, validators
import os.path as op
from allchat import app, db
from allchat.database.models import UserInfo, UserAuth, FriendList, GroupMember, GroupInfo
path = op.join(op.abspath(op.join(op.dirname(__file__), op.pardir, op.pardir)), 'static')

class AuthModelView(ModelView):
    def is_accessible(self):
        return 'admin' in session and session['admin'] == 'root'

class AuthFileAdmin(FileAdmin):
    def is_accessible(self):
        return 'admin' in session and session['admin'] == 'root'


class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None or user.username != 'root':
            raise validators.ValidationError('Invalid user')

        auth = db.session.query(UserAuth).filter_by(account=self.login.data).first()

        if not auth.is_authenticated(self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(UserInfo).filter_by(username=self.login.data).first()

class AuthAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not ('admin' in session and session['admin'] == 'root'):
            return redirect(url_for('.login_view'))
        return super(AuthAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            session.permanent = False
            session['admin'] = 'root'

        if 'admin' in session and session['admin'] == 'root':
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(AuthAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        session['admin'] = None
        del session['admin']
        return redirect(url_for('.index'))


admin = Admin(app, 'Auth', index_view=AuthAdminIndexView(), base_template='master.html')
admin.add_view(AuthModelView(UserInfo, db.session, name="UserInfo"))
admin.add_view(AuthModelView(UserAuth, db.session, name="UserAuth"))
admin.add_view(AuthModelView(FriendList, db.session, name="FriendList"))
admin.add_view(AuthModelView(GroupInfo, db.session, name="GroupInfo"))
admin.add_view(AuthModelView(GroupMember, db.session, name="GroupMember"))
admin.add_view(AuthFileAdmin(path, '/static/', name='Static Files'))
