from sqlalchemy import *
from sqlalchemy.orm import relationship, backref 
from sqlalchemy.ext.declarative import declarative_base
from socket import inet_pton,inet_ntop,AF_INET,AF_INET6
from struct import pack, unpack
import sqlalchemy.types as types
import hashlib
import bcrypt

engine = create_engine('sqlite:///data.db', echo=True)
Base = declarative_base()


class INetAddress(types.TypeDecorator):
    '''INET_ATON/NTOA Datatype
    '''

    impl = types.Binary

    def process_bind_param(self, value, dialect):
        _addr = inet_pton(AF_INET, value)
        return unpack('!L',_addr)
        

    def process_result_value(self, value, dialect):
        _addr = pack('!L', value)
        return inet_ntop(AF_INET, _addr)

    def copy(self):
        return INetAddress(self.impl.length)




class User(Base):
    __tablename__ = 'users'
    user = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    password = Column(String(128))
    streampassword = Column(String(128))
    shows = relationship('Show', secondary='user_shows', backref='users')
    
    PASS_MD5 = '1'
    PASS_BCRYPT = '2a'
    PASS_SHA1 = '3'
    
    def __init__(self, name, password, streampassword):
        self.name = name
        self.password = password
        self.streampassword = streampassword

    def checkPassword(self, password):
        p = self.password.split('$')
        print p
        if p[1] == User.PASS_BCRYPT :
            return bcrypt.hashpw(password, self.password) == self.password
        elif p[1] == User.PASS_MD5 :
            return hashlib.md5(password) == p[3]
        elif p[1] == User.PASS_SHA1 :
            return hashlib.sha1(password) == p[3]
    
    def checkUsername(self, username):
        if username.contains('|'):
            return False
        elif len(username) < 3:
            return False
        else:
            return True
    
    @staticmethod        
    def makePassword(password, encryption=PASS_BCRYPT):
        '''returns passwordstring $hashmethod$salt$hash'''
        salt = ''
        hash = ''
        if encryption == User.PASS_BCRYPT:
            return bcrypt.hashpw(password, bcrypt.gensalt())
        elif encryption == User.PASS_MD5:
            hash = hashlib.md5(password).hexdigest()
        elif encryption == User.PASS_SHA1:
            hash = hashlib.sha1(password).hexdigest()
        return '$%d$%s$%s' % (encryption, salt, hash)

class IRCUser(Base):
    __tablename__ = 'ircusers'
    ircuser = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    hostmask = Column(String(255))
    user_id = Column('user',Integer(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="RESTRICT"))
    user = relationship('User', backref='ircusers')

user_shows = Table('user_shows', Base.metadata,
     Column('user', Integer(unsigned=True), ForeignKey('users.user'), primary_key=True),
     Column('show', Integer(unsigned=True), ForeignKey('shows.show'), primary_key=True)
)

class Series(Base):
    __tablename__ = 'series'
    series = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(50))
    description = Column(Text)
    
class Show(Base):
    __tablename__ = 'shows'
    show = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    user = Column(Integer(unsigned=True), ForeignKey('users.user', onupdate="CASCADE", ondelete="RESTRICT"))
    series = Column(Integer(unsigned=True), ForeignKey('series.series', onupdate="CASCADE", ondelete="RESTRICT"))
    begin = Column(DateTime)
    end = Column(DateTime)
    name = Column(String(50))
    description = Column(Text)
    flags = Column(Integer(unsigned=True))
    
    SHOW_DELETED = 1
    SHOW_RECORD  = 2
    #users = relationship('User', secondary='user_shows', backref='shows')

class Artist(Base):
    __tablename__ = 'artists'
    artist = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(255))
    
class Title(Base):
    __tablename__ = 'titles'
    title = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    artist_id = Column('artist', Integer(unsigned=True), ForeignKey('artists.artist', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = relationship('Artist', backref='titles')
    name = Column(String(255))
    duration = Column(Integer)

class MetaArtist(Base):
    __tablename__ = 'metaArtists'
    metaArtist = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    artist_id = Column('artist', Integer(unsigned=True), ForeignKey('artists.artist', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = relationship('Artist', backref='metaArtists')
    
    name = Column(String(255))
    
class MetaTitle(Base):
    __tablename__ = 'metaTitles'
    metaTitle = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    title_id = Column('title', Integer(unsigned=True), ForeignKey('titles.title', onupdate="CASCADE", ondelete="RESTRICT"))
    title = relationship('Title', backref='metaTitles')
    
    name = Column(String(255))
    duration = Column(Integer(unsigned=True))
    durationWeight = Column(Integer(unsigned=True))
    
    def addDuration(self, duration):
        '''adds a new duration to this metaTitle'''
        self.duration = ((self.duration * self.durationWeight) + duration) / (self.durationWeight + 1)
        self.durationWeight += 1
        
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
    relay = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name  = Column(String(50))
    address = Column(INetAddress)
    port  = Column(Integer(unsigned=True))


class Stream(Base):
    __tablename__ = 'streams'
    stream = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    relays = relationship('Relay', backref='streams')

class Listener(Base):
    __tablename__ = 'listeners'
    listener = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    connect = Column(DateTime)
    disconnect = Column(DateTime)
    address = Column(INetAddress)

def createDB():
    Base.metadata.create_all(engine)

createDB()