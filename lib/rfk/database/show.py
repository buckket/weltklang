from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, exc
from sqlalchemy.sql.expression import between
from datetime import datetime
from rfk.database import Base
from rfk import ENUM, SET

class Show(Base):
    __tablename__ = 'shows'
    show = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column("series", Integer, ForeignKey('series.series',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    series = relationship("Series", backref=backref('shows'))
    logo = Column(String(255))
    begin = Column(DateTime)
    end = Column(DateTime)
    name = Column(String(50))
    description = Column(Text)
    flags = Column(Integer)
    FLAGS = SET(['DELETED','RECORD'])

    def add_tags(self, tags):
        for tag in tags:
            self.add_tag(tag=tag)
            
    def add_tag(self, tag=None, name=None):
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
    
    @staticmethod
    def get_current_show(user=None):
        query = Show.query.join(UserShow).filter(between(datetime.utcnow(), Show.begin, Show.end))
        if user:
            query = query.filter(UserShow.user == user)
        return query.first()
        

class UserShow(Base):
    __tablename__ = 'user_shows'
    userShow = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("user", Integer, ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref=backref('shows'))
    show_id = Column("show", Integer,
                           ForeignKey('shows.show',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    show = relationship("Show", backref=backref('users'))
    role_id = Column("role", Integer,
                           ForeignKey('roles.role',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    role = relationship("Role")
    status = Column(Integer)
    STATUS = ENUM(['UNKNOWN', 'STREAMING', 'STREAMED'])
    
    
class Tag(Base):
    __tablename__ = 'tags'
    tag = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(25))
    description = Column(Text)
    
    @staticmethod
    def get_tag(name):
        try:
            return Tag.query.filter(Tag.name == name).one()
        except exc.NoResultFound:
            return Tag(name=name,description=name)
    
    @staticmethod
    def parse_tags(tags):
        r = []
        for tag in tags.split(' '):
            r.append(Tag.get_tag(tag))
        return r

class ShowTag(Base):
    __tablename__ = 'show_tags'
    show_tag = Column(Integer, primary_key=True, autoincrement=True)
    show_id = Column("show", Integer,
                           ForeignKey('shows.show',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    show = relationship("Show", backref=backref('tags'))
    tag_id = Column("tag", Integer,
                           ForeignKey('tags.tag',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    tag = relationship("Tag", backref=backref('shows'))
    
    def __init__(self, tag):
        self.tag = tag
    
class Role(Base):
    __tablename__ = 'roles'
    role = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    
    
class Series(Base):
    __tablename__ = 'series'
    
    series = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("user", Integer, ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    user = relationship("User", backref=backref('series'))
    public = Column(Boolean)
    name = Column(String(50))
    description = Column(String(255))
    logo = Column(String(255))