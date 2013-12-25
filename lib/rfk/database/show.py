from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship, backref, exc
from sqlalchemy.sql.expression import between
from sqlalchemy.dialects.mysql import INTEGER as Integer 

from datetime import datetime
from rfk.database import Base, UTCDateTime
import rfk.database
from rfk.types import ENUM, SET

from rfk.helper import now

class Show(Base):
    """Show"""
    __tablename__ = 'shows'
    show = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    series_id = Column("series", Integer(unsigned=True), ForeignKey('series.series',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    series = relationship("Series", backref=backref('shows'))
    logo = Column(String(255))
    begin = Column(UTCDateTime, default=now)
    end = Column(UTCDateTime)
    updated = Column(UTCDateTime, default=now)
    name = Column(String(50))
    description = Column(Text)
    flags = Column(Integer(unsigned=True), default=0)
    FLAGS = SET(['DELETED', 'PLANNED', 'UNPLANNED', 'RECORD'])

    @hybrid_property
    def length(self):
        return self.end - self.begin

    @hybrid_method
    def contains(self,point):
        return (self.begin <= point) & (point < self.end)

    @hybrid_method
    def intersects(self, other):
        return self.contains(other.begin) | self.contains(other.end)
    
    def end_show(self):
        """ends the Show
           raises exception if the show is planned since it doesn't need to be ended"""
        if self.flags & Show.FLAGS.PLANNED:
            raise Exception
        self.end = now()
        rfk.database.session.flush()
        
    def add_tags(self, tags):
        """adds a list of Tags to the Show"""
        for tag in tags:
            self.add_tag(tag=tag)
    
    def sync_tags(self, tags):
        old_tags = []
        for tag in self.tags:
            old_tags.append(tag.tag)
        for tag in tags:
            if tag in old_tags:
                old_tags.remove(tag)
            self.add_tag(tag=tag)
        for tag in old_tags:
            ShowTag.query.filter(ShowTag.show == self,
                                 ShowTag.tag == tag).delete()
        rfk.database.session.flush()
            
    
    def add_tag(self, tag=None, name=None):
        """adds a Tag to the Show either by object or by identifier"""
        assert tag or name
        if tag is None:
            tag = Tag.get_tag(name)
        if tag is None:
            return False
        try:
            ShowTag.query.filter(ShowTag.show == self,
                                 ShowTag.tag == tag).one()
            return False
        except exc.NoResultFound:
            self.tags.append(ShowTag(tag))
            rfk.database.session.flush()
            return True
    
    def add_user(self, user, role=None):
        if role is None:
            role = Role.get_role('host')
        try:
            us = UserShow.query.filter(UserShow.user == user,
                                       UserShow.show == self).one()
            if us.role != role:
                us.role = role
            rfk.database.session.flush()
            return us
        except exc.NoResultFound:
            us = UserShow(show=self, user=user, role=role)
            rfk.database.session.add(us)
            rfk.database.session.flush()
            return us
            
    def remove_user(self, user):
        """removes the association to user"""
        UserShow.query.filter(UserShow.user == user,
                              UserShow.show == self).delete()
    
    def get_usershow(self, user):
        try:
            return UserShow.query.filter(UserShow.user == user,
                                         UserShow.show == self).one()
        except exc.NoResultFound:
            return None
    
    @staticmethod
    def get_current_show(user=None, only_planned=False):
        """returns the current show"""
        clauses = []
        clauses.append((between(datetime.utcnow(), Show.begin, Show.end)) | (Show.end == None))
        clauses.append(UserShow.user == user)
        if only_planned:
            clauses.append(Show.flags == Show.FLAGS.PLANNED)
        shows = Show.query.join(UserShow).filter(*clauses).all()
        if len(shows) == 1:
            return shows[0]
        elif len(shows) > 1:
            for show in shows:
                if show.flags & Show.FLAGS.PLANNED:
                    return show
            return shows[0]
        else:
            return None
    
    @staticmethod
    def get_active_show():
        try:
            return Show.query.join(UserShow).filter(UserShow.status == UserShow.STATUS.STREAMING).one()
        except exc.NoResultFound:
            return None
    
    def get_active_user(self):
        try:
            return UserShow.query.filter(UserShow.show == self,
                                         UserShow.status == UserShow.STATUS.STREAMING).one().user
        except exc.NoResultFound:
            return None
    
    def get_logo(self):
        """return the logourl for this show
           falls back to serieslogo if set"""
        if self.logo is not None:
            return self.logo
        elif self.series is not None:
            return self.series.logo
    
    def __repr__(self):
        return "<rfk.database.show.Show id=%d flags=%s name=%s >" % (self.show,Show.FLAGS.name(self.flags), self.name)

"""Show Indices"""
Index('show_begin_idx', Show.begin)
Index('show_end_idx', Show.end)


class UserShow(Base):
    """connection between users and show"""
    __tablename__ = 'user_shows'
    userShow = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column("user", Integer(unsigned=True), ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref=backref('shows', cascade="all, delete-orphan"))
    show_id = Column("show", Integer(unsigned=True),
                           ForeignKey('shows.show',
                                      onupdate="CASCADE",
                                      ondelete="CASCADE"), nullable=False)
    show = relationship("Show", backref=backref('users', cascade="all, delete-orphan"))
    role_id = Column("role", Integer(unsigned=True),
                           ForeignKey('roles.role',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"), nullable=False)
    role = relationship("Role")
    status = Column(Integer(unsigned=True), default=0)
    STATUS = ENUM(['UNKNOWN', 'STREAMING', 'STREAMED'])
    
    
class Tag(Base):
    __tablename__ = 'tags'
    tag = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(25), nullable=False, unique=True)
    icon = Column(String(30))
    description = Column(Text, nullable=False)
    
    @staticmethod
    def get_tag(name):
        """returns a Tag object by given identifier"""
        try:
            return Tag.query.filter(Tag.name == name).one()
        except exc.NoResultFound:
            tag = Tag(name=name,description=name)
            rfk.database.session.add(tag)
            rfk.database.session.flush()
            return tag
    
    @staticmethod
    def parse_tags(tags):
        """parses a space separated list of tags and returns a list of Tag objects"""
        def unique(seq):
            seen = set()
            seen_add = seen.add
            return [ x for x in seq if x not in seen and not seen_add(x)]
        r = []
        if tags is not None and len(tags) > 0:
            for str_tag in unique(tags.strip().split(' ')):
                if str_tag == '':
                    continue
                tag = Tag.get_tag(str_tag)
                r.append(tag)
        return r

class ShowTag(Base):
    """connection between Shows and Tags"""
    __tablename__ = 'show_tags'
    show_tag = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    show_id = Column("show", Integer(unsigned=True),
                           ForeignKey('shows.show',
                                      onupdate="CASCADE",
                                      ondelete="CASCADE"), nullable=False)
    show = relationship("Show", backref=backref('tags', cascade="all, delete-orphan"))
    tag_id = Column("tag", Integer(unsigned=True),
                           ForeignKey('tags.tag',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"), nullable=False)
    tag = relationship("Tag", backref=backref('shows', cascade="all, delete-orphan"))
    
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
            role = Role(name=name)
            rfk.database.session.add(role)
            rfk.database.session.flush()
            return role
    
    
class Series(Base):
    __tablename__ = 'series'
    
    series = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column("user", Integer(unsigned=True), ForeignKey('users.user',
                                                 onupdate="CASCADE",
                                                 ondelete="SET NULL"))
    user = relationship("User", backref=backref('series'))
    public = Column(Boolean)
    name = Column(String(50))
    description = Column(String(255))
    logo = Column(String(255))