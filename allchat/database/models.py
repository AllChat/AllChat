# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Table, Column, Integer, String, Enum, MetaData, ForeignKey, Unicode, Boolean, DateTime
# from sqlalchemy.orm import relationship, backref
# from sqlalchemy import ForeignKey
# from sqlalchemy import func
import datetime, hashlib, random, string
from allchat import app
from allchat import db

# Base = declarative_base()

class UserInfo(db.Model):
    __tablename__ = "userinfo"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), index = True, unique = True, nullable = False)
    nickname = db.Column(db.Unicode(50))
    password = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    state = db.Column(db.Enum('online', 'invisible', 'offline', name = 'state'), nullable = False)
    last_state = db.Column(db.Enum('online', 'invisible', 'offline', name = 'state'), nullable = False, default="offline")
    method = db.Column(db.Enum('web', 'mobile', 'desktop', name = 'method'))
    getunreadmsg = db.Column(db.Boolean, nullable = False, default = False)
    login = db.Column(db.DateTime(timezone = True))
    created = db.Column(db.DateTime(timezone = True), nullable = False)
    updated = db.Column(db.DateTime(timezone = True), nullable = False)
    deleted = db.Column(db.Boolean, nullable = False, default = False)
    ip = db.Column(db.String(15), nullable = False, default = "0.0.0.0")
    port = db.Column(db.Integer, nullable = False, default = 0)
    icon = db.Column(db.Integer, nullable = False, default = 0)

    friends = db.relationship('FriendList', cascade="all, delete-orphan", single_parent = True, passive_deletes=True, \
                              backref=db.backref('user', order_by=id), lazy="dynamic")
    
    def __init__(self, username, password, email, nickname = None, state = None, method = None, 
                getunreadmsg = False, login = None, created = None, updated = None, deleted = False, 
                ip = None, port = None, icon = None):
        self.username = username
        self.nickname = nickname
        self.email = email
        self.password = password
        if state is None:
            self.state = 'offline'
        else:
            self.state = state
        self.method = method
        self.getunreadmsg = getunreadmsg
        self.login = login
        self.created = datetime.datetime.utcnow() if not created else created
        self.updated = self.created if not updated else updated
        self.deleted = deleted
        self.ip = "0.0.0.0" if not ip else ip
        self.port = app.config["CLIENT_PORT"] if not port else port
        self.icon = int(icon) if (type(icon) == int) and (int(icon) >= 0) else 0

class UserAuth(db.Model):
    __tablename__ = "userauth"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }

    id = db.Column(db.Integer, primary_key = True)
    account = db.Column(db.String(50), index = True, unique = True, nullable = False)
    password = db.Column(db.String(64), nullable = False)
    salt = db.Column(db.String(16), nullable = False)
    prev_token = db.Column(db.String(32))
    token = db.Column(db.String(32))
    created = db.Column(db.DateTime(timezone = True), nullable = False)
    updated = db.Column(db.DateTime(timezone = True), nullable = False)
    deleted = db.Column(db.Boolean, nullable = False, default = False)


    def __init__(self, account, password):
        self.account = account
        self.salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        self.password = hashlib.sha256(self.salt+password).hexdigest()
        self.token = None
        self.prev_token = None
        self.created = datetime.datetime.utcnow()
        self.updated = self.created
        self.deleted = False

    def is_authenticated(self, password):
        if self.deleted == True:
            return False
        if password == hashlib.sha256(self.salt+password).hexdigest():
            db.session.begin(subtransactions=True)
            try:
                self.prev_token = self.token
                self.token = ''.join(random.sample(string.ascii_letters + string.digits, 32))
                self.updated = datetime.datetime.utcnow()
                db.session.add(self)
                db.session.commit()
            except:
                db.session.rollback()
                return False
            return True
        else:
            return False
    def is_token(self, token):
        if (self.deleted == True) or (token == None):
            return False
        if token == self.token:
            return True
        else:
            return False
    def is_prev_token(self, token):
        if (self.deleted == True) or (token == None):
            return False
        if token == self.prev_token:
            return True
        else:
            return False
    def fresh(self, token):
        if (self.deleted == False) and self.is_token(token):
            db.session.begin(subtransactions=True)
            try:
                self.prev_token = self.token
                self.token = ''.join(random.sample(string.ascii_letters + string.digits, 32))
                self.updated = datetime.datetime.utcnow()
                db.session.add(self)
                db.session.commit()
            except:
                db.session.rollback()
                return False
        return True
    def clear(self):
        db.session.begin(subtransactions=True)
        try:
            self.prev_token = None
            self.token = None
            self.updated = datetime.datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
            return False

    def delete(self):
        if(self.deleted == True):
            return True
        db.session.begin(subtransactions=True)
        try:
            self.deleted = True
            self.prev_token = None
            self.token = None
            self.updated = datetime.datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
            return False
        return True


    def activate(self, password):
        if self.deleted == False:
            return True
        if password == hashlib.sha256(self.salt+password).hexdigest():
            db.session.begin(subtransactions=True)
            try:
                self.deleted = False
                self.prev_token = None
                self.token = ''.join(random.sample(string.ascii_letters + string.digits, 32))
                self.updated = datetime.datetime.utcnow()
                db.session.add(self)
                db.session.commit()
            except:
                db.session.rollback()
                return False
        else:
            return False
        return True


class FriendList(db.Model):
    __tablename__ = "friendlist"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), index = True, nullable = False)
    nickname = db.Column(db.Unicode(50))
    state = db.Column(db.Enum('online', 'invisible', 'offline', name = 'state'), nullable = False)
    icon = db.Column(db.Integer, nullable = False, default = 0)
    confirmed = db.Column(db.Boolean, nullable = False, default = False)
    index = db.Column(db.Integer, db.ForeignKey('userinfo.id', onupdate="CASCADE", ondelete='CASCADE'), nullable = False)
    
    def __init__(self, username, nickname, state = None, confirmed = False, icon = None):
        self.username = username
        self.nickname = nickname
        if state is None:
            self.state = 'offline'
        else:
            self.state = state
        self.icon = int(icon) if (type(icon) == int) and (int(icon) >= 0) else 0
        self.confirmed = confirmed

class GroupInfo(db.Model):
    __tablename__ = "groupinfo"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }
    id = db.Column(db.Integer, primary_key = True)
    group_id = db.Column(db.Integer, nullable = False, index = True, unique = True)
    group_name = db.Column(db.Unicode(50))
    owner = db.Column(db.String(50), nullable = False)
    group_size = db.Column(db.Integer, nullable = False)
    group_volume = db.Column(db.Integer, nullable = False)
    created = db.Column(db.DateTime(timezone = True), nullable = False)
    updated = db.Column(db.DateTime(timezone = True), nullable = False)

    groupmembers = db.relationship('GroupMember', cascade="all, delete-orphan", single_parent = True, passive_deletes=True, \
                                   backref=db.backref('group', order_by=id), lazy="dynamic")
    
    def __init__(self, group_id, owner, group_name = None, group_size = 1, group_volume = 100, created = None, updated = None):
        self.group_id = group_id
        self.owner = owner
        self.group_name = group_name
        self.group_size = group_size
        self.group_volume = group_volume
        self.created = datetime.datetime.utcnow() if not created else created
        self.updated = self.created if not updated else updated

class GroupMember(db.Model):
    __tablename__ = "groupmember"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }
    id = db.Column(db.Integer, primary_key = True)
    group_id = db.Column(db.Integer, nullable = False)
    group_name = db.Column(db.Unicode(50))
    member_account = db.Column(db.String(50), index = True, nullable = False)
    nickname = db.Column(db.Unicode(50))
    icon = db.Column(db.Integer, nullable = False, default = 0)
    role = db.Column(db.Enum('owner', 'manager', 'member', name = 'role'), nullable = False)
    member_logstate = db.Column(db.Enum('online', 'invisible', 'offline', name = 'state'), nullable = False)
    confirmed = db.Column(db.Boolean, nullable = False, default = False)
    index = db.Column(db.Integer, db.ForeignKey('groupinfo.id', onupdate="CASCADE", ondelete='CASCADE'), nullable = False)

    def __init__(self, group_id, group_name, member_account, member_logstate, nickname, icon, role = "member", confirmed = False):
        self.group_id = group_id
        self.group_name = group_name
        self.member_account = member_account
        self.member_logstate = member_logstate
        self.nickname = nickname
        self.icon = icon
        self.role = role
        self.confirmed = confirmed
