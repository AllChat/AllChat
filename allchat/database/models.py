from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Enum, MetaData, ForeignKey, Unicode, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy import func
import datetime
from allchat import app

Base = declarative_base()

class UserInfo(Base):
    __tablename__ = "userinfo"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }
    
    id = Column(Integer, primary_key = True)
    username = Column(String(50), index = True, unique = True, nullable = False)
    nickname = Column(Unicode(50))
    password = Column(String(50), nullable = False)
    email = Column(String(100), nullable = False)
    state = Column(Enum('online', 'invisible', 'offline', name = 'state'), nullable = False)
    last_state = Column(Enum('online', 'invisible', 'offline', name = 'state'), nullable = False, default="offline")
    method = Column(Enum('web', 'mobile', 'desktop', name = 'method'))
    getunreadmsg = Column(Boolean, nullable = False, default = False)
    login = Column(DateTime(timezone = True))
    created = Column(DateTime(timezone = True), nullable = False)
    updated = Column(DateTime(timezone = True), nullable = False)
    deleted = Column(Boolean, nullable = False, default = False)
    ip = Column(String(15), nullable = False, default = "0.0.0.0")
    port = Column(Integer, nullable = False, default = 0)
    icon = Column(Integer, nullable = False, default = 0)

    friends = relationship('FriendList', cascade="all, delete-orphan", single_parent = True, passive_deletes=True, backref=backref('user', order_by=id))
    
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
        
class FriendList(Base):
    __tablename__ = "friendlist"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }
    id = Column(Integer, primary_key = True)
    username = Column(String(50), index = True, nullable = False)
    nickname = Column(Unicode(50))
    state = Column(Enum('online', 'invisible', 'offline', name = 'state'), nullable = False)
    icon = Column(Integer, nullable = False, default = 0)
    confirmed = Column(Boolean, nullable = False, default = False)
    index = Column(Integer, ForeignKey('userinfo.id', onupdate="CASCADE", ondelete='CASCADE'), nullable = False)
    
    def __init__(self, username, nickname, state = None, confirmed = False, icon = None):
        self.username = username
        self.nickname = nickname
        if state is None:
            self.state = 'offline'
        else:
            self.state = state
        self.icon = int(icon) if (type(icon) == int) and (int(icon) >= 0) else 0
        self.confirmed = confirmed

class GroupInfo(Base):
    __tablename__ = "groupinfo"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }
    id = Column(Integer, primary_key = True)
    group_id = Column(Integer, nullable = False, index = True, unique = True)
    group_name = Column(Unicode(50))
    owner = Column(String(50), nullable = False)
    group_size = Column(Integer, nullable = False)
    group_volume = Column(Integer, nullable = False)
    created = Column(DateTime(timezone = True), nullable = False)
    updated = Column(DateTime(timezone = True), nullable = False)

    groupmembers = relationship('GroupMember', cascade="all, delete-orphan", single_parent = True, passive_deletes=True, backref=backref('group', order_by=id))
    
    def __init__(self, group_id, owner, group_name = None, group_size = 1, group_volume = 100, created = None, updated = None):
        self.group_id = group_id
        self.owner = owner
        self.group_name = group_name
        self.group_size = group_size
        self.group_volume = group_volume
        self.created = datetime.datetime.utcnow() if not created else created
        self.updated = self.created if not updated else updated

class GroupMember(Base):
    __tablename__ = "groupmember"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_bin'
    }
    id = Column(Integer, primary_key = True)
    group_id = Column(Integer, nullable = False)
    group_name = Column(Unicode(50))
    member_account = Column(String(50), index = True, nullable = False)
    role = Column(Enum('owner', 'manager', 'member', name = 'role'), nullable = False)
    member_logstate = Column(Enum('online', 'invisible', 'offline', name = 'state'), nullable = False)
    confirmed = Column(Boolean, nullable = False, default = False)
    index = Column(Integer, ForeignKey('groupinfo.id', onupdate="CASCADE", ondelete='CASCADE'), nullable = False)

    def __init__(self, group_id, group_name, member_account, member_logstate, role = "member", confirmed = False):
        self.group_id = group_id
        self.group_name = group_name
        self.member_account = member_account
        self.member_logstate = member_logstate
        self.role = role
        self.confirmed = confirmed
