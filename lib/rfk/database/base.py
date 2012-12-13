from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session, exc
from passlib.hash import bcrypt
import hashlib
import re

from rfk.database import Base, session

class User(Base):
    __tablename__ = 'users'
    user = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    password = Column(String(64))
    mail = Column(String(255))
    
    def get_id(self):
        return unicode(self.user)
    
    def is_anonymous(self):
        return False
    
    def is_active(self):
        return True
    
    def is_authenticated(self):
        return True
    
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
    permission = Column(Integer, primary_key=True, autoincrement=True)
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
    userPermission = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("user", Integer, ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref=backref('permissions'))
    permission_id = Column("permission", Integer,
                           ForeignKey('permissions.permission',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    permission = relationship("Permission", backref=backref('users'))
    
    def __init__(self, permission):
        self.permission = permission
    
    
class Ban(Base):
    __tablename__ = 'bans'
    ban = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("user", Integer, ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref=backref('bans'))
    range = Column(String(50))
    expiration = Column(DateTime)
    
class News(Base):
    __tablename__ = 'news'
    news = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("user", Integer, ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User")
    title = Column(String(255))
    content = Column(Text)
    
    