from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, exc
from sqlalchemy.sql.expression import between
from sqlalchemy.dialects.mysql import INTEGER as Integer 

from datetime import datetime
from rfk.database import Base
from rfk import ENUM, SET

class Show(Base):
    """Show"""
    __tablename__ = 'shows'
    show = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    series_id = Column("series", Integer(unsigned=True), ForeignKey('series.series',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    series = relationship("Series", backref=backref('shows'))
    logo = Column(String(255))
    begin = Column(DateTime, default=datetime.utcnow)
    end = Column(DateTime)
    updated = Column(DateTime, default=datetime.utcnow)
    name = Column(String(50))
    description = Column(Text)
    flags = Column(Integer(unsigned=True), default=0)
    FLAGS = SET(['DELETED', 'PLANNED', 'UNPLANNED', 'RECORD'])

    def add_tags(self, tags):
        """ads a list of Tags to the Show"""
        for tag in tags:
            self.add_tag(tag=tag)
            
    def add_tag(self, tag=None, name=None):
        """adds a Tag to the Show either by object or by identifier"""
        assert tag or name
        if tag is None:
            tag = Tag.get_tag(name)
        try:
            ShowTag.query.filter(ShowTag.show == self,
                                 ShowTag.tag == tag).one()
            return False
        except exc.NoResultFound:
            self.tags.append(ShowTag(tag))
            return True
    
    def add_user(self, user, role=None):
        if role is None:
            role = Role.get_role('host')
        try:
            us = UserShow.query.filter(UserShow.user == user,
                                       UserShow.show == self).one()
            if us.role != role:
                us.role = role
            return us
        except exc.NoResultFound:
            return UserShow(show=self, user=user, role=role)
            
    def remove_user(self, user):
        UserShow.query.filter(UserShow.user == user,
                              UserShow.show == self).delete()
    
    @staticmethod
    def get_current_show(user=None):
        """returns the current show"""
        query = Show.query.join(UserShow).filter(or_(between(datetime.utcnow(), Show.begin, Show.end), Show.end == None))
        if user:
            query = query.filter(UserShow.user == user)
        return query.first()
    
    def __repr__(self):
        return "<rfk.database.show.Show id=%d>" % (self.show,)
        

class UserShow(Base):
    """connection between users and show"""
    __tablename__ = 'user_shows'
    userShow = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column("user", Integer(unsigned=True), ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref=backref('shows'))
    show_id = Column("show", Integer(unsigned=True),
                           ForeignKey('shows.show',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    show = relationship("Show", backref=backref('users'))
    role_id = Column("role", Integer(unsigned=True),
                           ForeignKey('roles.role',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    role = relationship("Role")
    status = Column(Integer(unsigned=True), default=0)
    STATUS = ENUM(['UNKNOWN', 'STREAMING', 'STREAMED'])
    
    
class Tag(Base):
    __tablename__ = 'tags'
    tag = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(25))
    description = Column(Text)
    
    @staticmethod
    def get_tag(name):
        """returns a Tag object by given identifier"""
        try:
            return Tag.query.filter(Tag.name == name).one()
        except exc.NoResultFound:
            return Tag(name=name,description=name)
    
    @staticmethod
    def parse_tags(tags):
        """parses a space separated list of tags and returns a list of Tag objects"""
        r = []
        if tags is not None and len(tags) > 0:
            for tag in tags.split(' '):
                r.append(Tag.get_tag(tag))
        return r

class ShowTag(Base):
    """connection between Shows and Tags"""
    __tablename__ = 'show_tags'
    show_tag = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    show_id = Column("show", Integer(unsigned=True),
                           ForeignKey('shows.show',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    show = relationship("Show", backref=backref('tags'))
    tag_id = Column("tag", Integer(unsigned=True),
                           ForeignKey('tags.tag',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    tag = relationship("Tag", backref=backref('shows'))
    
    def __init__(self, tag):
        self.tag = tag
    
class Role(Base):
    __tablename__ = 'roles'
    role = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(50))
    
    @staticmethod
    def get_role(name):
        try:
            return Role.query.filter(Role.name == name).one()
        except exc.NoResultFound:
            return Role(name=name)
    
    
class Series(Base):
    __tablename__ = 'series'
    
    series = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column("user", Integer(unsigned=True), ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref=backref('series'))
    public = Column(Boolean)
    name = Column(String(50))
    description = Column(String(255))
    logo = Column(String(255))