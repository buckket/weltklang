#!/usr/bin/python2.7
'''
Created on 30.04.2012

@author: teddydestodes
'''
import rfk
import os
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref,sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))

class Streamer(Base):
    __tablename__ = 'streamer'
    streamer = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    streampassword = Column(String)
    ban      = Column(DateTime) 

class Show(Base):
    __tablename__ = 'shows'
    show = Column(Integer, primary_key=True, autoincrement=True)
    streamer_id = Column('streamer', Integer(unsigned=True), ForeignKey('streamer.streamer', onupdate="CASCADE", ondelete="RESTRICT"))
    streamer = relationship('Streamer', backref='shows')
    songs = relationship('Song', backref='shows')
    name = Column(String)
    description = Column(String)
    begin = Column(DateTime)
    end = Column(DateTime)
    
class Song(Base):
    __tablename__ = 'songhistory'
    song = Column(Integer, primary_key=True, autoincrement=True)
    show_id = Column('show', Integer(unsigned=True), ForeignKey('shows.show', onupdate="CASCADE", ondelete="RESTRICT"))
    artist = Column(String)
    title = Column(String)
    begin = Column(DateTime)
    end = Column(DateTime)

mount_relay = Table('mount_relay', Base.metadata,
     Column('mount', Integer(unsigned=True), ForeignKey('mounts.mount')),
     Column('relay', Integer(unsigned=True), ForeignKey('relays.relay'))
)

class Mount(Base):
    __tablename__ = 'mounts'
    mount = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String)
    name = Column(String)
    description = Column(String)
    type = Column(String)
    quality = Column(Integer)
    username = Column(String)
    password = Column(String)
    relays = relationship('Relay', secondary='mount_relay', backref='mounts')
    
class Relay(Base):
    __tablename__ = 'relays'
    relay = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    hostname = Column(String)
    port = Column(String)
    status = Column(String)
    bandwidth = Column(Integer)
    query_method = Column(String)
    query_user = Column(String)
    query_pass = Column(String)
    
class Listener(Base):
    __tablename__ = 'listenerhistory'
    listenerhistory = Column(Integer, primary_key=True, autoincrement=True)
    mount_id = Column('mount', Integer(unsigned=True), ForeignKey('mounts.mount'))
    mount = relationship('Mount', backref='listenerhistory')
    relay_id = Column('relay', Integer(unsigned=True), ForeignKey('relays.relay'))
    relay = relationship('Relay', backref='listenerhistory')
    ip = Column(rfk.INetAddress)
    useragent = Column(String)
    connected = Column(DateTime)
    disconnected = Column(DateTime)
    client = Column(Integer)
    
old_engine = create_engine("%s://%s:%s@%s/%s?charset=utf8" % (rfk.config.get('olddatabase', 'engine'),
                                                              rfk.config.get('olddatabase', 'username'),
                                                              rfk.config.get('olddatabase', 'password'),
                                                              rfk.config.get('olddatabase', 'host'),
                                                              rfk.config.get('olddatabase', 'database')))
engine = create_engine("%s://%s:%s@%s/%s?charset=utf8" % (rfk.config.get('database', 'engine'),
                                                              rfk.config.get('database', 'username'),
                                                              rfk.config.get('database', 'password'),
                                                              rfk.config.get('database', 'host'),
                                                              rfk.config.get('database', 'database')))

rfk.Base.metadata.create_all(engine)

OldSession = sessionmaker(bind=old_engine)
oldsession = OldSession()
Session = sessionmaker(bind=engine)
session = Session()

def copy_users():
    streamer = oldsession.query(Streamer).yield_per(50)
    
    for olduser in streamer:
        print olduser.username
        user = session.query(rfk.User).filter(rfk.User.name == olduser.username).first()
        if user == None:
            user = rfk.User(olduser.username, olduser.password, rfk.User.makePassword(olduser.streampassword))
            session.add(user)
    session.commit()
    
    
def copy_shows():
    shows = oldsession.query(Show).yield_per(50)
    for oldshow in shows:
        print oldshow.show
        show = rfk.Show(name=oldshow.name, description=oldshow.description, begin=oldshow.begin, end=oldshow.end)
        if oldshow.streamer != None:
            user = session.query(rfk.User).filter(rfk.User.name == oldshow.streamer.username).first()
            show.users.append(user)
        session.add(show)
        
        for oldsong in oldshow.songs:
            title = rfk.Title.checkTitle(session, oldsong.artist, oldsong.title, begin=oldsong.begin, end=oldsong.end)
            song = rfk.Song(begin=oldsong.begin, end=oldsong.end)
            song.show = show
            song.title = title
            session.add(song)
    session.commit()

def copy_mounts():
    relays = oldsession.query(Relay).yield_per(50)
    for oldrelay in relays:
        print oldrelay.type
        qm = rfk.Relay.QUERY_VNSTAT
        if oldrelay.query_method == 'REMOTE_ICECAST2_KH':
            qm = rfk.Relay.QUERY_ICECAST_KH
            
        type = rfk.Relay.TYPE_MASTER
        if oldrelay.query_method == 'RELAY':
            type = rfk.Relay.TYPE_RELAY
        relay = rfk.Relay(name=oldrelay.hostname,
                          hostname=oldrelay.hostname,
                          port=oldrelay.port,
                          queryMethod=qm,
                          queryUsername=oldrelay.query_user,
                          queryPassword=oldrelay.query_pass,
                          bandwidth=oldrelay.bandwidth,
                          status=rfk.Relay.STATUS_OFFLINE,
                          type=type,
                          traffic=0)
        session.add(relay)
    mounts = oldsession.query(Mount).all()
    for oldmount in mounts:
        type = 0
        if oldmount.type == 'LAMEVBR':
            type = rfk.Stream.TYPE_MP3
        elif oldmount.type == 'AACP':
            type = rfk.Stream.TYPE_AACP
        elif oldmount.type == 'OGG':
            type = rfk.Stream.TYPE_OGG
            
        mount = rfk.Stream(mountpoint=oldmount.path,
                           name=oldmount.name,
                           description=oldmount.description,
                           type=type,
                           quality=oldmount.quality,
                           username=oldmount.username,
                           password=oldmount.password)
        for oldrelay in oldmount.relays:
            relay = session.query(rfk.Relay).filter(rfk.Relay.hostname==oldrelay.hostname).first()
            mount.relays.append(relay)
        session.add(mount)
    session.commit()

def copy_listener():
    listeners = oldsession.query(Listener).yield_per(50)
    
    
    for oldlistener in listeners:
        mount = session.query(rfk.Stream).filter(rfk.Stream.name==oldlistener.mount.name).first()
        relay = session.query(rfk.Relay).filter(rfk.Relay.hostname == oldlistener.relay.hostname).first()
        listener = rfk.Listener(connect = oldlistener.connected,
                                disconnect = oldlistener.disconnected,
                                address = oldlistener.ip,
                                useragent = oldlistener.useragent,
                                relay    = relay,
                                stream   = mount,
                                client = oldlistener.client)
        session.add(listener)
    session.commit()

if __name__ == '__main__':
    #copy_users()
    #copy_shows()
    #copy_mounts()
    #copy_listener()
    mounts = oldsession.query(Mount).all()
    for oldmount in mounts:
        type = 0
        if oldmount.type == 'LAMEVBR':
            type = rfk.Stream.TYPE_MP3
        elif oldmount.type == 'AACP':
            type = rfk.Stream.TYPE_AACP
        elif oldmount.type == 'OGG':
            type = rfk.Stream.TYPE_OGG
        
        print type
        
        