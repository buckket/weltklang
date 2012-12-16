from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, exc
from sqlalchemy.dialects.mysql import INTEGER as Integer

from rfk.database import Base

class Track(Base):
    __tablename__ = 'tracks'
    track = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    
class Title(Base):
    __tablename__ = 'titles'
    title = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    
class MetaTitle(Base):
    __tablename__ = 'metatitles'
    metatitle = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    
class Artist(Base):
    __tablename__ = 'artists'
    artist = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    
class MetaArtist(Base):
    __tablename__ = 'metaartists'
    metaartist = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)