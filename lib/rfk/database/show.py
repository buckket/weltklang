from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, exc

from rfk.database import Base

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
    
    
class Tag(Base):
    __tablename__ = 'tags'
    tag = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(25))
    description = Column(Text)
    
    
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