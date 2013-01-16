from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session, exc
from sqlalchemy.dialects.mysql import INTEGER as Integer 

from passlib.hash import bcrypt
from flask.ext.login import AnonymousUser
from rfk import SET
from rfk import exc as rexc
from datetime import datetime, timedelta
import time
import hashlib
import re

from rfk.database import Base, session


class Anonymous(AnonymousUser):
    
    def __init__(self):
        AnonymousUser.__init__(self)
        self.locale = 'de'
        self.timezone = 'Europe/Berlin'

class User(Base):
    __tablename__ = 'users'
    user = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    password = Column(String(64))
    mail = Column(String(255))
    country = Column(String(3))
    
    def get_id(self):
        return unicode(self.user)
    
    def is_anonymous(self):
        return False
    
    def is_active(self):
        return True
    
    def is_authenticated(self):
        return True
    
    @staticmethod
    def get_user(id=None, username=None):
        assert id or username
        try:
            if username is None:
                return User.query.filter(User.user == id).one()
            else:
                return User.query.filter(User.username == username).one()
        except exc.NoResultFound:
            return None
                
    @staticmethod
    def check_username(username):
        if re.match('^[0-9a-zA-Z_-]{3,}$', username) == None:
            return False
        else:
            return True
    
    @staticmethod
    def make_password(password):
        return bcrypt.encrypt(password)
    
    @staticmethod
    def add_user(username, password):
        try:
            return User.query.filter(User.username == username).one()
        except exc.NoResultFound:
            return User(username=username, password=User.make_password(password))
    
    def check_password(self, password):
        try:
            return bcrypt.verify(password, self.password)
        except ValueError:
            if hashlib.sha1(password).hexdigest() == self.password:
                self.password = User.make_password(password)
                return True
            else:
                return False
            
    def add_permission(self, code=None, permission=None):
        assert code or permission
        if permission is None:
            permission = Permission.get_permission(code)
        try:
            UserPermission.query.filter(UserPermission.user == self,
                                        UserPermission.permission == permission)\
                                        .one()
            return False
        except exc.NoResultFound:
            self.permissions.append(UserPermission(permission))
            return True
        
    def has_permission(self, code=None, permission=None):
        assert code or permission
        if permission is None:
            permission = Permission.get_permission(code)
        try:
            UserPermission.query.filter(UserPermission.user == self,
                                        UserPermission.permission == permission)\
                                        .one()
            return True
        except exc.NoResultFound:
            return False


class Permission(Base):
    __tablename__ = 'permissions'
    permission = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    code = Column(String(25), unique=True)
    name = Column(String(50))

    @staticmethod
    def get_permission(code):
        return Permission.query.filter(Permission.code == code).one()
    
    @staticmethod
    def add_permission(code,name):
        try:
            return Permission.query.filter(Permission.code == code).one()
        except exc.NoResultFound:
            return Permission(code=code, name=name)

class UserPermission(Base):
    __tablename__ = 'user_permissions'
    userPermission = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column("user", Integer(unsigned=True), ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref=backref('permissions'))
    permission_id = Column("permission", Integer(unsigned=True),
                           ForeignKey('permissions.permission',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    permission = relationship("Permission", backref=backref('users'))
    
    def __init__(self, permission):
        self.permission = permission
    
    
class Ban(Base):
    __tablename__ = 'bans'
    ban = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column("user", Integer(unsigned=True), ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref=backref('bans'))
    range = Column(String(50))
    expiration = Column(DateTime)
    
class News(Base):
    __tablename__ = 'news'
    news = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column("user", Integer(unsigned=True), ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User")
    title = Column(String(255))
    content = Column(Text)
    
class ApiKey(Base):
    __tablename__ = 'apikeys'
    apikey = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column("user", Integer(unsigned=True), ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref="apikeys")
    key = Column(String(128))
    counter = Column(Integer(unsigned=True), default=0)
    access = Column(DateTime, default=datetime.utcnow)
    application = Column(String(128))
    description = Column(String(255))
    flag = Column(Integer(unsigned=True), default=0)
    FLAGS = SET(['DISABLED', 'FASTQUERY', 'KICK', 'BAN', 'AUTH'])
        
    def gen_key(self):
        c = 0
        while True:
            key = hashlib.sha1("%s%s%d%d" % (self.application, self.description, time.time(), c)).hexdigest()
            if ApiKey.query.filter(ApiKey.key == key).first() == None:
                break
        self.key = key
    
    @staticmethod
    def check_key(key):
        
        try:
            apikey = ApiKey.query.filter(ApiKey.key==key).one()
        except (exc.NoResultFound, exc.MultipleResultsFound):
            raise rexc.api.KeyInvalidException()
        if apikey.flag & ApiKey.FLAGS.DISABLED:
            raise rexc.api.KeyDisabledException()
        elif not apikey.flag & ApiKey.FLAGS.FASTQUERY:
            if datetime.utcnow() - apikey.access <= timedelta(seconds=1):
                raise rexc.api.FastQueryException(last_access=apikey.access)
    
        apikey.counter += 1
        apikey.access = datetime.utcnow()
        return apikey
    