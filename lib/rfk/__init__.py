from sqlalchemy.orm import relationship, mapper
from sqlalchemy import Table
from ConfigParser import SafeConfigParser
from itertools import count, izip
from collections import OrderedDict, Set
import os
CONFIG = SafeConfigParser()



class SET(Set):
    """An OrderedFrozenSet-like object
       Allows constant time 'index'ing
       But doesn't allow you to remove elements"""
    def __init__(self, iterable = ()):
        self.num = count()
        self.dict = OrderedDict(izip(iterable, self.num))
    def add(self, elem):
        if elem not in self:
            self.dict[elem] = next(self.num)
    def index(self, elem):
        return self.dict[elem]
    def __contains__(self, elem):
        return elem in self.dict
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        return iter(self.dict)
    def __repr__(self):
        return 'IndexOrderedSet({})'.format(self.dict.keys())
    def __getattr__(self, name):
        if name in self:
            return 1<<(self.index(name))
        raise AttributeError
    def name(self,mask):
        for elem in self:
            if mask & 1<<self.index(elem):
                return elem

class ENUM(Set):
    """An OrderedFrozenSet-like object
       Allows constant time 'index'ing
       But doesn't allow you to remove elements"""
    def __init__(self, iterable = ()):
        self.num = count()
        self.dict = OrderedDict(izip(iterable, self.num))
    def add(self, elem):
        if elem not in self:
            self.dict[elem] = next(self.num)
    def index(self, elem):
        return self.dict[elem]
    def __contains__(self, elem):
        return elem in self.dict
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        return iter(self.dict)
    def __repr__(self):
        return 'IndexOrderedSet({})'.format(self.dict.keys())
    def __getattr__(self, name):
        if name in self:
            return self.index(name)
        raise AttributeError

from rfk.model import *

def init(basepath):
    CONFIG.read(os.path.join(basepath, 'etc', 'config.cfg'))

def init_db(engine, metadata):
    """initializes Database
    """
    users = Table('users',
                  metadata, autoload=True, autoload_with=engine)
    user_shows = Table('user_shows',
                       metadata, autoload=True, autoload_with=engine)
    shows = Table('shows',
                  metadata, autoload=True, autoload_with=engine)
    show_tags = Table('show_tags',
                      metadata, autoload=True, autoload_with=engine)
    tags = Table('tags',
                 metadata, autoload=True, autoload_with=engine)
    series = Table('series',
                   metadata, autoload=True, autoload_with=engine)
    user_settings = Table('user_settings',
                          metadata, autoload=True, autoload_with=engine)
    settings = Table('settings',
                     metadata, autoload=True, autoload_with=engine)
    user_permissions = Table('user_permissions',
                             metadata, autoload=True, autoload_with=engine)
    permissions = Table('permissions',
                        metadata, autoload=True, autoload_with=engine)
    ircusers = Table('ircusers',
                     metadata, autoload=True, autoload_with=engine)
    apikeys = Table('apikeys',
                    metadata, autoload=True, autoload_with=engine)
    news = Table('news',
                 metadata, autoload=True, autoload_with=engine)
    songs = Table('songs',
                  metadata, autoload=True, autoload_with=engine)
    titles = Table('titles',
                   metadata, autoload=True, autoload_with=engine)
    metatitles = Table('metaTitles',
                       metadata, autoload=True, autoload_with=engine)
    artists = Table('artists',
                    metadata, autoload=True, autoload_with=engine)
    metaartists = Table('metaArtists',
                        metadata, autoload=True, autoload_with=engine)
    playlist = Table('playlist',
                     metadata, autoload=True, autoload_with=engine)
    relays = Table('relays',
                     metadata, autoload=True, autoload_with=engine)
    stream_relays = Table('stream_relays',
                     metadata, autoload=True, autoload_with=engine)
    streams = Table('streams',
                     metadata, autoload=True, autoload_with=engine)
    listeners = Table('listeners',
                     metadata, autoload=True, autoload_with=engine)
    show_listener = Table('show_listener',
                     metadata, autoload=True, autoload_with=engine)
    mapper(Playlist, playlist)
    mapper(MetaTitle, metatitles)
    mapper(Stream, streams)
    mapper(Relay, relays, properties={
                        'streams': relationship(Stream,
                                    secondary=stream_relays,
                                    backref='relays.relay')})
    mapper(StreamRelay, stream_relays, properties={
                        'stream_id': stream_relays.c.stream,
                        'relay_id': stream_relays.c.relay,
                        'stream': relationship(Stream),
                        'relay': relationship(Relay)})
    mapper(Listener,listeners, properties={
                'relay_id': listeners.c.relay,
                'stream_id': listeners.c.stream,
                'relay': relationship(Relay, backref='listeners.listener'),
                'stream': relationship(Stream, backref='listeners.listener'),
                'shows': relationship(Show,
                                      secondary=show_listener,
                                      backref='listeners.listener')
                                    })
    mapper(ShowListener,show_listener, properties={
                        'listener_id': show_listener.c.listener,
                        'show_id': show_listener.c.show,
                        'listener': relationship(Listener),
                        'show': relationship(Show)})
    mapper(Title, titles, properties={
                'metatitles': relationship(MetaTitle, backref='titles.title')})
    
    mapper(MetaArtist, metaartists)
    mapper(Artist, artists, properties={
                'metaartists': relationship(MetaArtist,
                                            backref='artists.artist')})
    
    mapper(Song, songs)
    mapper(Tag, tags)
    mapper(Series, series, properties={'shows': relationship(Show,
                                       backref='series.series')})
    mapper(Show, shows, properties={
                'songs': relationship(Song,
                                      backref='shows.show'),
                'tags': relationship(Tag,
                                     secondary=show_tags, backref='shows.show')
                                    })
    
    mapper(Setting, settings)
    mapper(Permission, permissions)
    mapper(IrcUser, ircusers)
    mapper(ApiKey, apikeys)
    mapper(News, news)
    
    mapper(User, users, properties={
                'settings': relationship(Setting,
                                         secondary=user_settings,
                                         backref='users.user'),
                'ircuser': relationship(IrcUser,
                                        backref='users.user'),
                'apikeys': relationship(ApiKey,
                                        backref='users.user'),
                'news': relationship(News,
                                     backref='users.user'),
                'permissions': relationship(Permission,
                                     secondary=user_permissions)
                                    })

    mapper(UserShow, user_shows, properties={
                'user_id': user_shows.c.user,
                'show_id': user_shows.c.show,
                'user': relationship(User,
                                      backref='user_shows'),
                'show': relationship(Show,
                                      backref='user_shows')})
    mapper(UserPermission, user_permissions, properties={
                'user_id': user_permissions.c.user,
                'permission_id': user_permissions.c.permission,
                'user': relationship(User),
                'permission': relationship(Permission)
                                                         })