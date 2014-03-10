from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Enum, MetaData, ForeignKey, Unicode, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.databases import mysql
import datetime


Base = declarative_base()

class UserInfo(Base):
    __tablename__ = "userinfo"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    
    id = Column(Integer, primary_key = True)
    username = Column(String(50), index = True, unique = True, nullable = False)
    nickname = Column(Unicode(50))
    password = Column(String(50), nullable = False)
    state = Column(Enum(('online', 'invisible', 'offline')), nullable = False)
    method = Column(Enum(('web', 'mobile', 'desktop')))
    getunreadmsg = Column(Boolean, nullable = False, default = False)
    login = Column(DateTime(timezone = True))
    created = Column(DateTime(timezone = True), nullable = False)
    updated = Column(DateTime(timezone = True), nullable = False)
    deleted = Column(Boolean, nullable = False, default = False)
    
    groups = relationship('GroupList', backref=backref('users', order_by=id))
    friends = relationship('FriendList', backref=backref('users', order_by=id))
    
    def __init__(self, username, password, nickname = None, state = None, method = None, 
                getunreadmsg = False, login = None, created = None, updated = None, deleted = False):
        self.username = username
        self.nickname = nickname
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
        
class GroupList(Base):
    pass
    
class FriendList(Base):
    pass

class GroupInfo(Base):
    __tablename__ = "userinfo"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
