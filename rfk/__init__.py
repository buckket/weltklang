from sqlalchemy import *
from sqlalchemy.orm import relationship, backref 
from sqlalchemy.ext.declarative import declarative_base
from socket import inet_pton, inet_ntop, AF_INET, AF_INET6
from struct import pack, unpack
from time import time
from ConfigParser import SafeConfigParser
import sqlalchemy.types as types
import hashlib
import bcrypt


import os, os.path
 
import cherrypy
from cherrypy.process import wspbus, plugins



Base = declarative_base()

config = SafeConfigParser()

class INetAddress(types.TypeDecorator):
    '''INET_ATON/NTOA Datatype
    '''

    impl = types.Integer

    def process_bind_param(self, value, dialect):
        _addr = inet_pton(AF_INET, value)
        return unpack('!L', _addr)[0]
        

    def process_result_value(self, value, dialect):
        _addr = pack('!L', value)
        return inet_ntop(AF_INET, _addr)

    def copy(self):
        return INetAddress(self)




class User(Base):
    __tablename__ = 'users'
    user = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    password = Column(String(128))
    streampassword = Column(String(128))
    shows = relationship('Show', secondary='user_shows', backref='users')
    
    def __init__(self, name, password, streampassword):
        self.name = name
        self.password = password
        self.streampassword = streampassword

    def checkPassword(self, password):
        try:
            return bcrypt.hashpw(password, self.password) == self.password
        except ValueError:
            if hashlib.sha1(password) == self.password :
                self.password = User.makePassword(password)
                return True
            else:
                return False
    
    def checkUsername(self, username):
        if username.contains('|'):
            return False
        elif len(username) < 3:
            return False
        else:
            return True
    
    @staticmethod        
    def makePassword(password):
        return bcrypt.hashpw(password, bcrypt.gensalt())

class IRCUser(Base):
    __tablename__ = 'ircusers'
    ircuser = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    hostmask = Column(String(255))
    user_id = Column('user', Integer(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="RESTRICT"))
    user = relationship('User', backref='ircusers')

user_shows = Table('user_shows', Base.metadata,
     Column('user', Integer(unsigned=True), ForeignKey('users.user'), primary_key=True),
     Column('show', Integer(unsigned=True), ForeignKey('shows.show'), primary_key=True),
     Column('role', Integer(unsigned=True))
)

class Series(Base):
    __tablename__ = 'series'
    series = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(50))
    description = Column(Text)
    
class Show(Base):
    __tablename__ = 'shows'
    show = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    series = Column(Integer(unsigned=True), ForeignKey('series.series', onupdate="CASCADE", ondelete="RESTRICT"))
    begin = Column(DateTime)
    end = Column(DateTime)
    name = Column(String(50))
    description = Column(Text)
    flags = Column(Integer(unsigned=True))
    
    SHOW_DELETED   = 1
    SHOW_RECORD    = 2
    SHOW_PLANNED   = 4
    SHOW_UNPLANNED = 8
    #users = relationship('User', secondary='user_shows', backref='shows')

class Artist(Base):
    __tablename__ = 'artists'
    artist = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(255))
    
    @staticmethod
    def checkArtist(session, artist):
        metaArtist = session.query(MetaArtist).filter(MetaArtist.name==artist).first()
        if metaArtist == None :
            metaArtist = MetaArtist(name=artist)
            session.add(metaArtist)
            art = Artist(name=artist)
            session.add(art)
            metaArtist.artist = art
        return metaArtist.artist

class Title(Base):
    __tablename__ = 'titles'
    title = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    artist_id = Column('artist', Integer(unsigned=True), ForeignKey('artists.artist', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = relationship('Artist', backref='titles')
    name = Column(String(255))
    duration = Column(Integer)
    
    @staticmethod
    def checkTitle(session,artist, title, begin=None, end=None):
        metaTitle = session.query(MetaTitle).filter(MetaTitle.name==title).join(Title).join(Artist).join(MetaArtist).filter(MetaArtist.name==artist).first()
        if metaTitle == None :
            metaTitle = MetaTitle(name=title)
            session.add(metaTitle)
            tit = Title(name=title)
            tit.artist = Artist.checkArtist(session, artist)
            metaTitle.title = tit
            session.add(tit)
        if begin != None and end != None:
            metaTitle.addDuration(begin, end)
        return metaTitle.title

class MetaArtist(Base):
    __tablename__ = 'metaArtists'
    metaArtist = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    artist_id = Column('artist', Integer(unsigned=True), ForeignKey('artists.artist', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = relationship('Artist', backref='metaArtists')
    name = Column(String(255), unique=True)
    
class MetaTitle(Base):
    __tablename__ = 'metaTitles'
    metaTitle = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    title_id = Column('title', Integer(unsigned=True), ForeignKey('titles.title', onupdate="CASCADE", ondelete="RESTRICT"))
    title = relationship('Title', backref='metaTitles')
    
    name = Column(String(255))
    duration = Column(Integer(unsigned=True))
    durationWeight = Column(Integer(unsigned=True))
    
    def addDuration(self, begin, end):
        '''adds a new duration to this metaTitle'''
        diff = end-begin
        duration = diff.days*86400+diff.seconds
        if self.durationWeight > 0 :
            self.duration = ((self.duration * self.durationWeight) + duration) / (self.durationWeight + 1)
            self.durationWeight += 1
        else :
            self.duration = duration
            self.durationWeight = 1
        
class Song(Base):
    __tablename__ = 'songs'
    song = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    begin = Column(DateTime)
    end = Column(DateTime)
    title_id = Column('title', Integer(unsigned=True), ForeignKey('titles.title', onupdate="CASCADE", ondelete="RESTRICT"))
    title = relationship('Title', backref='songs')
    show_id = Column('show', Integer(unsigned=True), ForeignKey('shows.show', onupdate="CASCADE", ondelete="RESTRICT"))
    show = relationship('Show', backref='songs')

stream_relays = Table('stream_relays', Base.metadata,
     Column('stream', Integer(unsigned=True), ForeignKey('streams.stream'), primary_key=True),
     Column('relay', Integer(unsigned=True), ForeignKey('relays.relay'), primary_key=True)
)

class Relay(Base):
    __tablename__ = 'relays'
    relay    = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name     = Column(String(50))
    hostname = Column(String(128))
    port     = Column(Integer(unsigned=True))
    type     = Column(Integer)
    bandwidth = Column(Integer)
    traffic   = Column(Integer)
    status    = Column(Integer)
    queryMethod = Column(Integer)
    queryUsername = Column(String(50))
    queryPassword = Column(String(50))
    
    TYPE_MASTER = 1
    TYPE_RELAY = 2
    
    STATUS_OFFLINE = 0
    STATUS_ONLINE = 1
    
    QUERY_VNSTAT = 1
    QUERY_ICECAST_KH = 2


class Stream(Base):
    __tablename__ = 'streams'
    stream = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    relays = relationship('Relay', secondary='stream_relays', backref='streams')
    mountpoint    = Column(String(50))
    name          = Column(String(50))
    description   = Column(String(50))
    type          = Column(Integer)
    quality       = Column(Integer)
    username      = Column(String(50))
    password      = Column(String(50))
    
    TYPE_MP3 = 1
    TYPE_AACP = 2
    TYPE_OGG = 2

class Listener(Base):
    __tablename__ = 'listeners'
    listener = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    connect = Column(DateTime)
    disconnect = Column(DateTime)
    address = Column(INetAddress)
    useragent = Column(String)
    relay_id = Column('relay', Integer(unsigned=True), ForeignKey('relays.relay', onupdate="CASCADE", ondelete="RESTRICT"))
    relay    = relationship('Relay', backref='listeners')
    stream_id = Column('stream', Integer(unsigned=True), ForeignKey('streams.stream', onupdate="CASCADE", ondelete="RESTRICT"))
    stream    = relationship('Stream', backref='listeners')
    client = Column(Integer)
    
class ApiKey(Base):
    __tablename__ = 'apikeys'
    apikey = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    application = Column(String(128))
    description = Column(Text)
    key         = Column(String(128), unique=True)
    user_id     = Column('user', Integer(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="CASCADE"))
    user        = relationship('User', backref='apikeys')
    flag        = Column(Integer(unsigned=True))
    def __init__(self, application, description, user):
        self.application = application
        self.description = description
        self.user = user
        self.flag = 0
        
    def genKey(self):
        key = hashlib.sha1("%s%s%d"%(self.application, self.description, time()))
        