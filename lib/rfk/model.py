'''
Created on Aug 28, 2012

@author: teddydestodes
'''
import hashlib
from passlib.hash import bcrypt
import datetime
import time
import re
from rfk import SET, ENUM
from sqlalchemy.orm import exc
from sqlalchemy import func, and_, or_, between

class User(object):
    STATUS = ENUM(['NONE','STREAMING'])
    
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
        return session.query(UserPermission).join(Permission).filter(UserPermission.user == self, Permission.code == 'admin').one()
    
    def check_password(self, session, password):
        try:
            return bcrypt.verify(password, self.password)
        except ValueError:
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
    
    @staticmethod
    def check_username(username):
        if re.match('^[0-9a-zA-Z_-]{3,}$', username) == None:
            return False
        else:
            return True
    
    def get_stream_time(self, session):
        time = session.query(User, func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin))))).join(UserShow).join(Show).filter(Show.end != None, User.user == self.user, Show.begin <= datetime.datetime.today()).group_by(User.user).order_by(func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin)))).desc()).first()
        if time == None:
            return datetime.timedelta(0)
        else:
            return time[1]
    
    def connect(self, session):
        session.query(User).filter(User.status == User.STATUS_STREAMING).update(status=User.STATUS_STREAMING)
        self.status = User.STATUS_STREAMING
        
    def disconnect(self):
        self.status = User.STATUS.NONE
        
    @staticmethod        
    def make_password(password):
        return bcrypt.encrypt(password)
    
    @staticmethod
    def get_top_user_by_show(session):
        return session.query(User, func.count()).join(UserShow).join(Show).group_by(User.user).order_by(func.count().desc())[:50]
    @staticmethod
    def get_top_user_by_show_length(session):
        return session.query(User, func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin))))).join(UserShow).join(Show).filter(Show.end != None).group_by(User.user).order_by(func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Show.end, Show.begin)))).desc())[:50]
    

class IrcUser(object):
    
    def __init__(self, user, hostmask):
        self.user = user
        self.hostmask = hostmask


class UserShow(object):
    
    def __init__(self, user, show):
        self.user = user
        self.show = show


class Show(object):
    
    FLAGS = SET([ 'DELETED',
                  'RECORD',
                  'PLANNED',
                  'UNPLANNED'])
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.begin = datetime.datetime.now()
        self.updated = datetime.datetime.now()
        
    @staticmethod
    def get_current_shows(session, user=None):
        clauses = []
        clauses.append(and_(Show.begin <= datetime.datetime.today(), or_(Show.end >= datetime.datetime.today(), Show.end == None)))
        if user != None:
            clauses.append(User.user == user.user)
        return session.query(Show).join(UserShow).join(User).filter(*clauses).order_by(Show.begin.desc(), Show.end.asc()).all()
    
    def end_show(self, now=datetime.datetime.today()):
        if self.end == None:
            self.end = now
        for song in self.songs:
            if song.end == None:
                song.end = now
        
    def get_user_role(self, session, user):
        return session.query(UserShow).filter_by(show=self.show, user=user.user).first()[2]
    
    def get_listener(self, session):
        return session.query(Listener).filter(self.begin < Listener.disconnect, self.end > Listener.connect).all()
    
    def update_tags(self, session, tags):
        newtags = Tag.parseTags(session, tags)
        for tag in newtags:
            if tag not in self.tags:
                self.tags.append(tag)
        for tag in self.tags:
            if tag not in newtags:
                self.tags.remove(tag)


class Setting(object):
    
    def __init__(self, code, name):
        self.code = code
        self.name = name


class UserPermission(object):
    
    def __init__(self, permission):
        self.permission = permission
        
    def has_permission(self, permission):
        print self.permission


class Permission(object):
    
    def __init__(self, code, name):
        self.code = code
        self.name = name
        
    @staticmethod
    def get_permission(session, code):
        return session.query(Permission).filter(Permission.code == code).one()


class ApiKey(object):
    
    FLAGS = SET(['DISABLED', 'FASTQUERY', 'KICK', 'BAN', 'AUTH'])

    def __init__(self, user, application):
        self.user = user
        self.application = application
        self.access = datetime.datetime.now()
        
    def gen_key(self, session):
        c = 0
        while True:
            key = hashlib.sha1("%s%s%d%d" % (self.application, self.description, time.time(), c)).hexdigest()
            if session.query(ApiKey).filter(ApiKey.key == key).first() == None:
                break
        self.key = key
    
    @staticmethod
    def check_key(key, session):
        try:
            apikey = session.query(ApiKey).filter(ApiKey.key==key).one()
        except (exc.NoResultFound, exc.MultipleResultsFound):
            return False
        if apikey.flag & ApiKey.FLAGS.DISABLED:
            return False
        elif not apikey.flag & ApiKey.FLAGS.FASTQUERY:
            if datetime.datetime.now() - apikey.access <= datetime.timedelta(seconds=1):
                return False
    
        apikey.counter += 1
        apikey.access = datetime.datetime.now()
        session.commit()
        return apikey
    

class News(object):
    
    def __init__(self, user, title, content):
        self.user = user
        self.title = title
        self.content = content
        self.time = datetime.datetime.now()
        
        
class Song(object):
    
    def __init__(self, show, title):
        self.show = show
        self.title = title
    
    @staticmethod
    def begin_song(session, begin, artist, title, show):
        song = Song.get_current_cong(session)
        if song:
            song.endSong(session)
        
        title = Title.check_title(session, artist, title, begin)
        song = Song(begin=begin, title=title, show=show)
        return song

    def end_song(self, session):
        self.end = datetime.datetime.today()
        #ohh gawd, i failed at desining the database
        #Title.checkTitle(session, self.title., title, self.end,self.end)
    
    @staticmethod
    def get_current_song(session):
        return session.query(Song).filter(Song.end == None).order_by(Song.song.desc()).first()

   
class Title(object):
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


class MetaTitle(object):
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


class Artist(object):
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


class MetaArtist(object):
    pass


class ShowTag(object):
    
    def __init__ (self, show, tag):
        self.show = show
        self.tag = tag


class Tag(object):
    
    def __init__(self, name):
        self.name = name

    @staticmethod
    def parse_tags(session, tags):
        r = []
        for tag in tags.split(' '):
            t = session.query(Tag).filter(Tag.name == tag).first()
            if t == None:
                t = Tag(tag)
                session.add(t)
            r.append(t)
        return r


class Series(object):
    pass


class Listener(object):
    
    @staticmethod
    def set_disconnected(session, relay, stream, client):
        listener = session.query(Listener).filter(and_(Listener.relay == relay, Listener.stream == stream, Listener.client == client, Listener.disconnect == None)).first()
        listener.disconnect = datetime.datetime.today()


class ShowListener(object):
    def __init__(self, show, listener):
        self.show = show
        self.listener = listener
        
        
class Stream(object):
    
    TYPES = ENUM(['UNKNOWN', 'MP3', 'AACP', 'OGG', 'OPUS'])
    
    def get_url(self, relay):
        return "http://%s:%d%s" % (relay.hostname, relay.port, self.mountpoint)
    
    def add(self, session, relay):
        session.query(Listener).filter(and_(Listener.relay == relay, Listener.stream == self, Listener.disconnect == None)).update({Listener.disconnect: datetime.datetime.today()})
        
    def remove(self, session, relay):
        session.query(Listener).filter(and_(Listener.relay == relay, Listener.stream == self, Listener.disconnect == None)).update({Listener.disconnect: datetime.datetime.today()})


class Relay(object):
    
    STATUS = ENUM(['UNKNOWN', 'DISABLED', 'OFFLINE', 'ONLINE'])
    TYPE = ENUM(['MASTER', 'RELAY'])
    QUERY_METHOD = ENUM(['LOCAL', 'ICECAST'])
    
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

   
class StreamRelay(object):
    
    def __init__(self, blah):
        pass

    
class Playlist(object):
    
    @staticmethod
    def get_current_item(session):
        all = session.query(Playlist).filter(between(datetime.datetime.today().time(), Playlist.begin, Playlist.end)).order_by(func.sec_to_time(func.sum(func.time_to_sec(func.timediff(Playlist.end, Playlist.begin)))).asc()).first()
        return all

