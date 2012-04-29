from sqlalchemy import *
from sqlalchemy.orm import relationship, backref 
from sqlalchemy.ext.declarative import declarative_base
import hashlib
import bcrypt

engine = create_engine('sqlite:///data.db', echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    password = Column(String(64))
    streampassword = Column(String(64))
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
            return bcrypt.hashpw(password,self.password) == self.password
        elif p[1] == User.PASS_MD5 :
            return hashlib.md5(password) == p[3]
        elif p[1] == User.PASS_SHA1 :
            return hashlib.sha1(password) == p[3]

@staticmethod        
def makePassword(password, encryption=User.PASS_BCRYPT):
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
    
User.makePassword = makePassword

user_shows = Table('user_shows', Base.metadata,
     Column('user', Integer, ForeignKey('users.user'), primary_key=True),
     Column('show', Integer, ForeignKey('shows.show'), primary_key=True)
)

class Show(Base):
    __tablename__ = 'shows'
    show = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(Integer, ForeignKey('users.user', onupdate="CASCADE", ondelete="RESTRICT"))
    name = Column(String(50))
    description = Column(Text)
    #users = relationship('User', secondary='user_shows', backref='shows')

class Artist(Base):
    __tablename__ = 'artists'
    artist = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    
class Title(Base):
    __tablename__ = 'titles'
    title = Column(Integer, primary_key=True, autoincrement=True)
    artist_id = Column('artist', Integer, ForeignKey('artists.artist', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = relationship('Artist', backref='titles')
    name = Column(String(255))
    duration = Column(Integer)

class MetaArtist(Base):
    __tablename__ = 'metaArtists'
    metaArtist = Column(Integer, primary_key=True, autoincrement=True)
    artist_id = Column('artist', Integer, ForeignKey('artists.artist', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = relationship('Artist', backref='metaArtists')
    
    name = Column(String(255))
    
class MetaTitle(Base):
    __tablename__ = 'metaTitles'
    metaTitle = Column(Integer, primary_key=True, autoincrement=True)
    title_id = Column('title', Integer, ForeignKey('titles.title', onupdate="CASCADE", ondelete="RESTRICT"))
    title = relationship('Title', backref='metaTitles')
    
    name = Column(String(255))
    duration = Column(Integer)
    durationWeight = Column(Integer)
    
    def addDuration(self, duration):
        '''adds a new duration to this metaTitle'''
        self.duration = ((self.duration * self.durationWeight) + duration) / (self.durationWeight + 1)
        self.durationWeight += 1
        
class Song(Base):
    __tablename__ = 'songs'
    song = Column(Integer, primary_key=True, autoincrement=True)
    begin = Column(DateTime)
    end = Column(DateTime)
    title_id = Column('title', Integer, ForeignKey('titles.title', onupdate="CASCADE", ondelete="RESTRICT"))
    title = relationship('Title', backref='songs')
    show_id = Column('show', Integer, ForeignKey('shows.show', onupdate="CASCADE", ondelete="RESTRICT"))
    show = relationship('Show', backref='songs')

class Relay(Base):
    __tablename__ = 'relays'
    relay = Column(Integer, primary_key=True, autoincrement=True)

class Stream(Base):
    __tablename__ = 'stream'
    stream = Column(Integer, primary_key=True, autoincrement=True)

def createDB():
    Base.metadata.create_all(engine)
