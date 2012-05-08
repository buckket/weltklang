from sqlalchemy import *
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship, backref 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.compiler import compiles
from socket import inet_pton, inet_ntop, AF_INET, AF_INET6
from struct import pack, unpack
from time import time
import datetime
from ConfigParser import SafeConfigParser
import sqlalchemy.types as types
import hashlib
import bcrypt


import os, os.path
 
import cherrypy
from cherrypy.process import wspbus, plugins
from jinja2 import Environment, FileSystemLoader


Base = declarative_base()
config = SafeConfigParser()

env = None

def initEnv(dir):
    Environment(loader=FileSystemLoader(dir))


class INetAddress(types.TypeDecorator):
    '''INET_ATON/NTOA Datatype
    '''

    impl = types.INTEGER
    
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(INTEGER(unsigned=True))

    def process_bind_param(self, value, dialect):
        _addr = inet_pton(AF_INET, value)
        return unpack('!L', _addr)[0]
        

    def process_result_value(self, value, dialect):
        _addr = pack('!L', value)
        return inet_ntop(AF_INET, _addr)




class User(Base):
    __tablename__ = 'users'
    user = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
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
    
    @staticmethod
    def getTopUserByShow(session):
        return session.query(User, func.count()).join(user_shows).join(Show).group_by(User.user).order_by(func.count().desc())[:50]
    @staticmethod
    def getTopUserByShowLength(session):
        return session.query(User, func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin))))).join(user_shows).join(Show).filter(Show.end != None).group_by(User.user).order_by(func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin)))).desc())[:50]
    
    
class IRCUser(Base):
    __tablename__ = 'ircusers'
    ircuser = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    hostmask = Column(String(255))
    user_id = Column('user', INTEGER(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="RESTRICT"))
    user = relationship('User', backref='ircusers')

user_shows = Table('user_shows', Base.metadata,
     Column('user', INTEGER(unsigned=True), ForeignKey('users.user'), primary_key=True),
     Column('show', INTEGER(unsigned=True), ForeignKey('shows.show'), primary_key=True),
     Column('role', INTEGER(unsigned=True))
)

class Series(Base):
    __tablename__ = 'series'
    series = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(50))
    description = Column(Text)
    
class Show(Base):
    __tablename__ = 'shows'
    show = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    series = Column(INTEGER(unsigned=True), ForeignKey('series.series', onupdate="CASCADE", ondelete="RESTRICT"))
    begin = Column(DateTime)
    end = Column(DateTime)
    name = Column(String(50))
    description = Column(Text)
    flags = Column(INTEGER(unsigned=True))
    
    SHOW_DELETED = 1
    SHOW_RECORD = 2
    SHOW_PLANNED = 4
    SHOW_UNPLANNED = 8
    #users = relationship('User', secondary='user_shows', backref='shows')
    
    @staticmethod
    def getCurrentShow(session, user=None):
        qry = session.query(Show).filter(and_(Show.begin >= datetime.datetime.today(), or_(Show.end <= datetime.datetime.today(), Show.end == None)))
        if user != None:
            qry.join('user_shows').join(User).filter(User == user)
        qry.order_by(Show.end.desc())
        return qry.all()
    
    def getListener(self, session):
        return session.query(Listener).join(Show).filter(and_(Show.show==self.show,and_(Show.begin < Listener.disconnect) and (Show.end > Listener.connect))).all()

class Artist(Base):
    __tablename__ = 'artists'
    artist = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(255))
    flags  = Column(INTEGER(unsigned=True))
    @staticmethod
    def getTopArtists(session):
        return session.query(Artist, func.count()).join(Title).join(Song).group_by(Artist.artist).order_by(func.count().desc())[:50]
    
    @staticmethod
    def checkArtist(session, artist):
        metaArtist = session.query(MetaArtist).filter(MetaArtist.name == artist).first()
        if metaArtist == None :
            metaArtist = MetaArtist(name=artist)
            session.add(metaArtist)
            art = Artist(name=artist)
            session.add(art)
            metaArtist.artist = art
        return metaArtist.artist

class Title(Base):
    __tablename__ = 'titles'
    title = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    artist_id = Column('artist', INTEGER(unsigned=True), ForeignKey('artists.artist', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = relationship('Artist', backref='titles')
    name = Column(String(255))
    duration = Column(INTEGER(unsigned=True))
    flags  = Column(INTEGER(unsigned=True))
    @staticmethod
    def getTopTitles(session):
        return session.query(Title, func.count()).join(Song).group_by(Title.title).order_by(func.count().desc())[:50]
    @staticmethod
    def checkTitle(session, artist, title, begin=None, end=None):
        metaTitle = session.query(MetaTitle).join(Title).join(Artist).join(MetaArtist).filter(and_(MetaTitle.name == title, MetaArtist.name == artist)).first()
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
    metaArtist = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    artist_id = Column('artist', INTEGER(unsigned=True), ForeignKey('artists.artist', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = relationship('Artist', backref='metaArtists')
    name = Column(String(255), unique=True)
    
class MetaTitle(Base):
    __tablename__ = 'metaTitles'
    metaTitle = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    title_id = Column('title', INTEGER(unsigned=True), ForeignKey('titles.title', onupdate="CASCADE", ondelete="RESTRICT"))
    title = relationship('Title', backref='metaTitles')
    
    name = Column(String(255))
    duration = Column(INTEGER(unsigned=True))
    durationWeight = Column(INTEGER(unsigned=True))
    
    def addDuration(self, begin, end):
        '''adds a new duration to this metaTitle'''
        diff = end - begin
        duration = diff.days * 86400 + diff.seconds
        if self.durationWeight > 0 :
            self.duration = ((self.duration * self.durationWeight) + duration) / (self.durationWeight + 1)
            self.durationWeight += 1
        else :
            self.duration = duration
            self.durationWeight = 1
        
class Song(Base):
    __tablename__ = 'songs'
    song = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    begin = Column(DateTime)
    end = Column(DateTime)
    title_id = Column('title', INTEGER(unsigned=True), ForeignKey('titles.title', onupdate="CASCADE", ondelete="RESTRICT"))
    title = relationship('Title', backref='songs')
    show_id = Column('show', INTEGER(unsigned=True), ForeignKey('shows.show', onupdate="CASCADE", ondelete="RESTRICT"))
    show = relationship('Show', backref='songs')
    
stream_relays = Table('stream_relays', Base.metadata,
     Column('stream', INTEGER(unsigned=True), ForeignKey('streams.stream'), primary_key=True),
     Column('relay', INTEGER(unsigned=True), ForeignKey('relays.relay'), primary_key=True)
)

class Relay(Base):
    __tablename__ = 'relays'
    relay = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(50))
    hostname = Column(String(128))
    port = Column(INTEGER(unsigned=True))
    type = Column(INTEGER(unsigned=True))
    bandwidth = Column(INTEGER(unsigned=True))
    traffic = Column(INTEGER(unsigned=True))
    status = Column(INTEGER(unsigned=True))
    queryMethod = Column(INTEGER(unsigned=True))
    queryUsername = Column(String(50))
    queryPassword = Column(String(50))
    
    TYPE_MASTER = 1
    TYPE_RELAY = 2
    
    STATUS_OFFLINE = 0
    STATUS_ONLINE = 1
    
    QUERY_VNSTAT = 1
    QUERY_ICECAST_KH = 2
    
    def getLoad(self):
        return (self.traffic / self.bandwith)
    
    @staticmethod
    def getBestRelay(session):
        relays = session.query(Relay).all()
        minLoad = 1
        bestRelay = None
        for relay in relays:
            if relay.getLoad() < minLoad:
                minLoad = relay.getLoad()
                bestRelay = relay
        return bestRelay
        

class Stream(Base):
    __tablename__ = 'streams'
    stream = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    relays = relationship('Relay', secondary='stream_relays', backref='streams')
    mountpoint = Column(String(50))
    name = Column(String(50))
    description = Column(String(50))
    type = Column(INTEGER(unsigned=True))
    quality = Column(INTEGER)
    username = Column(String(50))
    password = Column(String(50))
    
    TYPE_MP3 = 1
    TYPE_AACP = 2
    TYPE_OGG = 2
    
    def getURL(self, session):
        relay = Relay.getBestRelay(session)
        return "http://%s:%d%s" % (relay.hostname, relay.port, self.mountpoint)

class Listener(Base):
    __tablename__ = 'listeners'
    listener = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    connect = Column(DateTime)
    disconnect = Column(DateTime)
    address = Column(INetAddress)
    useragent = Column(String(255))
    relay_id = Column('relay', INTEGER(unsigned=True), ForeignKey('relays.relay', onupdate="CASCADE", ondelete="RESTRICT"))
    relay = relationship('Relay', backref='listeners')
    stream_id = Column('stream', INTEGER(unsigned=True), ForeignKey('streams.stream', onupdate="CASCADE", ondelete="RESTRICT"))
    stream = relationship('Stream', backref='listeners')
    client = Column(INTEGER(unsigned=True))
    
class ApiKey(Base):
    __tablename__ = 'apikeys'
    apikey = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    application = Column(String(128))
    description = Column(Text)
    key = Column(String(128), unique=True)
    user_id = Column('user', INTEGER(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="CASCADE"))
    user = relationship('User', backref='apikeys')
    flag = Column(INTEGER(unsigned=True))
    def __init__(self, application, description, user):
        self.application = application
        self.description = description
        self.user = user
        self.flag = 0
        
    def genKey(self):
        key = hashlib.sha1("%s%s%d" % (self.application, self.description, time()))
        
