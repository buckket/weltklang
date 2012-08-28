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
from passlib.hash import bcrypt


import os, os.path


Base = declarative_base()
config = SafeConfigParser()

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
    status = Column(INTEGER(unsigned=True))

    STATUS_NONE = 0
    STATUS_STREAMING = 1

    def __init__(self, name, password, streampassword):
        self.name = name
        self.password = password
        self.streampassword = streampassword
        self.authenticated = False
    
    def get_id(self):
        return unicode(self.user)
    
    def is_anonymous(self):
        return False
    
    def is_active(self):
        return True
    
    def is_authenticated(self):
        return True
    
    def is_admin(self, session):
        result = session.query(UserSetting).filter(UserSetting.user_id == self.user).filter(UserSetting.key == 'admin').filter(UserSetting.value == 'true').first()
        if result:
            return True
        else:
            return False
    
    def check_password(self, session, password):
        try:
            return bcrypt.verify(password, self.password)
        except ValueError:
            print  hashlib.sha1(password).hexdigest()
            if hashlib.sha1(password).hexdigest() == self.password:
                self.password = User.makePassword(password)
                session.commit()
                return True
            else:
                return False
    
    @staticmethod
    def get_user(session, username=None, id=None):
        if username:
            return session.query(User).filter(User.name == username).first()
        elif id:
            return session.query(User).get(id)
        return None
    
    def check_stream_password(self, password):
        return bcrypt.verify(password, self.streampassword)

    def check_username(self, username):
        if username.contains('|'):
            return False
        elif len(username) < 3:
            return False
        else:
            return True
    
    def get_stream_time(self, session):
        time = session.query(User, func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin))))).join(user_shows).join(Show).filter(Show.end != None, User.user == self.user, Show.begin <= datetime.datetime.today()).group_by(User.user).order_by(func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin)))).desc()).first()
        if time == None:
            return datetime.timedelta(0)
        else:
            return time[1]
    
    def connect(self, session):
        session.query(User).filter(User.status == User.STATUS_STREAMING).update(status=User.STATUS_STREAMING)
        self.status = User.STATUS_STREAMING
        
    def disconnect(self):
        self.status = User.STATUS_NONE
        
    @staticmethod        
    def make_password(password):
        return bcrypt.encrypt(password)
    
    @staticmethod
    def get_top_user_by_show(session):
        return session.query(User, func.count()).join(user_shows).join(Show).group_by(User.user).order_by(func.count().desc())[:50]
    @staticmethod
    def get_top_user_by_show_length(session):
        return session.query(User, func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin))))).join(user_shows).join(Show).filter(Show.end != None).group_by(User.user).order_by(func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin)))).desc())[:50]
    
class UserSetting(Base):
    __tablename__ = 'usersettings'
    usersetting = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column('user', INTEGER(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="RESTRICT"))
    user = relationship('User', backref='usersettings')
    key = Column(String(255))
    value = Column(String(255))
    
class News(Base):
    __tablename__ = 'news'
    news = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    time = Column(DateTime)
    user_id = Column('user', INTEGER(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="RESTRICT"))
    user = relationship('User', backref='news')
    title = Column(String(255))
    content = Column(Text)

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

class Tag(Base):
    __tablename__ = 'tags'
    tag = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = name = Column(String(50), unique=True)

    @staticmethod
    def parse_tags(session, tags):
        r = []
        for tag in tags.split(' '):
            t = session.query(Tag).filter(Tag.name == tag).first()
            if t == None:
                t = Tag(name=tag)
                session.add(t)
            r.append(t)
        return r
    
show_tags = Table('show_tags', Base.metadata,
     Column('show', INTEGER(unsigned=True), ForeignKey('shows.show'), primary_key=True),
     Column('tag', INTEGER(unsigned=True), ForeignKey('tags.tag'), primary_key=True),
)

show_listener = Table('show_listener', Base.metadata,
     Column('show', INTEGER(unsigned=True), ForeignKey('shows.show'), primary_key=True),
     Column('listener', INTEGER(unsigned=True), ForeignKey('listeners.listener'), primary_key=True),
)

class Show(Base):
    __tablename__ = 'shows'
    show = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    series = Column(INTEGER(unsigned=True), ForeignKey('series.series', onupdate="CASCADE", ondelete="RESTRICT"))
    begin = Column(DateTime)
    end = Column(DateTime)
    name = Column(String(50))
    description = Column(Text)
    tags = relationship('Tag', secondary='show_tags', backref='shows')
    listeners = relationship('Listener', secondary='show_listener', backref='shows')
    flags = Column(INTEGER(unsigned=True))
    
    
    SHOW_DELETED = 1
    SHOW_RECORD = 2
    SHOW_PLANNED = 4
    SHOW_UNPLANNED = 8
    
    @staticmethod
    def get_current_shows(session, user=None):
        clauses = []
        clauses.append(and_(Show.begin <= datetime.datetime.today(), or_(Show.end >= datetime.datetime.today(), Show.end == None)))
        if user != None:
            clauses.append(User.user == user.user)
        return session.query(Show).join(user_shows).join(User).filter(*clauses).order_by(Show.begin.desc(),Show.end.asc()).all()
    
    def end_show(self,now=datetime.datetime.today()):
        if self.end == None:
            self.end = now
        for song in self.songs:
            if song.end == None:
                song.end = now
        
    def get_user_role(self, session, user):
        return session.query(user_shows).filter_by(show=self.show, user=user.user).first()[2]
    
    def get_listener(self, session):
        return session.query(Listener).filter(self.begin < Listener.disconnect,self.end > Listener.connect).all()
    
    def update_tags(self, session, tags):
        newtags = Tag.parseTags(session, tags)
        for tag in newtags:
            if tag not in self.tags:
                self.tags.append(tag)
        for tag in self.tags:
            if tag not in newtags:
                self.tags.remove(tag)

class Artist(Base):
    __tablename__ = 'artists'
    artist = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(255))
    flags = Column(INTEGER(unsigned=True))
    
    @staticmethod
    def get_top_artists(session):
        return session.query(Artist, func.count()).join(Title).join(Song).group_by(Artist.artist).order_by(func.count().desc())[:50]
    
    @staticmethod
    def check_artist(session, artist):
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
    flags = Column(INTEGER(unsigned=True))
    
    @staticmethod
    def get_top_titles(session):
        return session.query(Title, func.count()).join(Song).group_by(Title.title).order_by(func.count().desc())[:50]
    
    @staticmethod
    def check_title(session, artist, title, begin=None, end=None):
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
    duration_weight = Column(INTEGER(unsigned=True))
    
    def add_duration(self, begin, end):
        '''adds a new duration to this metaTitle'''
        diff = end - begin
        duration = diff.days * 86400 + diff.seconds
        if self.duration_weight > 0 :
            self.duration = ((self.duration * self.duration_weight) + duration) / (self.duration_weight + 1)
            self.duration_weight += 1
        else :
            self.duration = duration
            self.duration_weight = 1
        
class Song(Base):
    __tablename__ = 'songs'
    song = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    begin = Column(DateTime)
    end = Column(DateTime)
    title_id = Column('title', INTEGER(unsigned=True), ForeignKey('titles.title', onupdate="CASCADE", ondelete="RESTRICT"))
    title = relationship('Title', backref='songs')
    show_id = Column('show', INTEGER(unsigned=True), ForeignKey('shows.show', onupdate="CASCADE", ondelete="RESTRICT"))
    show = relationship('Show', backref='songs')
    
    @staticmethod
    def begin_song(session,begin,artist,title,show):
        song = Song.getCurrentSong(session)
        if song:
            song.endSong(session)
        
        title = Title.checkTitle(session, artist, title, begin)
        song = Song(begin=begin, title=title, show=show)
        return song

    def end_song(self,session):
        self.end = datetime.datetime.today()
        #ohh gawd, i failed at desining the database
        #Title.checkTitle(session, self.title., title, self.end,self.end)
    
    @staticmethod
    def get_current_song(session):
        return session.query(Song).filter(Song.end == None).order_by(Song.song.desc()).first()
    
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
    query_method = Column(INTEGER(unsigned=True))
    query_username = Column(String(50))
    query_password = Column(String(50))
    
    TYPE_MASTER = 1
    TYPE_RELAY = 2
    
    STATUS_OFFLINE = 0
    STATUS_ONLINE = 1
    
    QUERY_VNSTAT = 1
    QUERY_ICECAST_KH = 2
    
    def get_load(self):
        return (self.traffic / self.bandwith)
    
    @staticmethod
    def get_best_relay(session):
        relays = session.query(Relay).filter(Relay.status == Relay.STATUS_ONLINE).all()
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
    TYPE_OGG = 3
    TYPE_OPUS = 4
    
    def get_url(self, relay):
        return "http://%s:%d%s" % (relay.hostname, relay.port, self.mountpoint)
    
    def add(self, session, relay):
        session.query(Listener).filter(and_(Listener.relay == relay, Listener.stream == self, Listener.disconnect == None)).update({Listener.disconnect: datetime.datetime.today()})
        
    def remove(self, session, relay):
        session.query(Listener).filter(and_(Listener.relay == relay, Listener.stream == self, Listener.disconnect == None)).update({Listener.disconnect: datetime.datetime.today()})


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
    
    @staticmethod
    def set_disconnected(session, relay, stream, client):
        listener = session.query(Listener).filter(and_(Listener.relay == relay, Listener.stream == stream, Listener.client == client, Listener.disconnect == None)).first()
        listener.disconnect = datetime.datetime.today()
        
class ApiKey(Base):
    __tablename__ = 'apikeys'
    apikey = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    application = Column(String(128))
    description = Column(Text)
    key = Column(String(128), unique=True)
    user_id = Column('user', INTEGER(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="CASCADE"))
    user = relationship('User', backref='apikeys')
    flag = Column(INTEGER(unsigned=True))
    
    FLAG_DISABLED  = 1
    FLAG_VIEWIP    = 2
    FLAG_FASTQUERY = 4
    FLAG_KICK      = 8
    FLAG_BAN       = 16
    FLAG_AUTH      = 32
    
    def __init__(self, application, description, user):
        self.application = application
        self.description = description
        self.user = user
        self.flag = 0
        
    def gen_key(self, session):
        c = 0
        while True:
            key = hashlib.sha1("%s%s%d%d" % (self.application, self.description, time(), c)).hexdigest()
            if session.query(ApiKey).filter(ApiKey.key==key).first() == None:
                break
        self.key = key
    
    @staticmethod
    def check_key(key, session):
        '''
        Checks an Apikey for exsistence
        @todo: other stuff like ratelimiting
        '''
        apikey = session.query(ApiKey).filter(ApiKey.key==key).first()
        if apikey != None:
            return True
        else:
            return False
        
class Playlist(Base):
    __tablename__ = 'playlist'
    playlist = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    begin = Column(Time)
    end = Column(Time)
    file = Column(String(128))
    
    @staticmethod
    def get_current_item(session):
        all = session.query(Playlist).filter(between(datetime.datetime.today().time(),Playlist.begin,Playlist.end)).order_by(func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Playlist.end, Playlist.begin)))).asc()).first()
        return all
