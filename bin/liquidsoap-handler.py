#!/usr/bin/python2.7
'''
Created on 06.05.2012

@author: teddydestodes

Flow is like this:

Auth: streamingclient tries to authenticate
Connect: streaming starts
Meta: Metadata (ATTENTION: not all clients send metadata!)
Disconnect: streamingclient disconnects

'''

import argparse
import json
import os
import sys
import base64
from datetime import datetime
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(basedir,'lib'))

import rfk
import rfk.database 
from rfk.database.base import User, Log
from rfk.database.show import Show, Tag, UserShow
from rfk.database.track import Track
from rfk.database.streaming import Listener
from rfk.liquidsoap import LiquidInterface
from rfk import exc as rexc

username_delimiter = '|'


def log(message):
    """shorthand method for writing log to database
    
    Keyword arguments:
    message -- string to write
    
    """
    log = Log(message=message)
    rfk.database.session.add(log)
    rfk.database.session.commit()

def kick():
    """shorthand method for kicking the currently connected user
    
    returns True if someone was kicked  
    """
    liquidsoap = LiquidInterface()
    liquidsoap.connect()
    kicked = False
    for source in liquidsoap.get_sources():
        if source.status() != 'no source client connected':
            source.kick()
            kicked = True
    liquidsoap.close()
    return kicked
    
def init_show(user, name="", description="", tags=""):
    """inititalizes a show
        it either takes a planned show or an unplanned show if it's still running
        if non of them is found a new unplanned show is added and initialized
        if a new show was initialized the old one will be ended and the streamer staus will be resettet
    """
    show = Show.get_current_show(user)
    if show is None:
        show = Show()
        show.add_tags(Tag.parse_tags(tags))
        show.description = description
        show.name = name
        show.flags = Show.FLAGS.UNPLANNED
        show.add_user(user)
    us = show.get_usershow(user)
    us.status = UserShow.STATUS.STREAMING
    rfk.database.session.flush()
    unfinished_shows = UserShow.query.filter(UserShow.status == UserShow.STATUS.STREAMING,
                                             UserShow.show != show).all()
    for us in unfinished_shows:
        if us.show.flags & Show.FLAGS.UNPLANNED:
            us.show.end_show()
        if us.status == UserShow.STATUS.STREAMING:
           us.status = UserShow.STATUS.STREAMED
        rfk.database.flush() 
    return show
        
def doAuth(username, password):
    """authenticates the user
    this function will also disconnect the current user
    if the user to be authenticated has a show registered.
    if that happened this function will print false to the
    user since we need a graceperiod to actually disconnect
    the other user.
    
    Keyword arguments:
    username
    password
    
    """
    if username == 'source':
        username, password = password.split(username_delimiter)
    try:
        user = User.authenticate(username, password)
        show = Show.get_current_show(user)
        if show is not None and show.flags & Show.FLAGS.PLANNED:
            if kick():
                log('kicked user')
                sys.stdout.write('false')
                return
        log('accepted auth for %s' %(username,))
        sys.stdout.write('true')
        return
    except rexc.base.InvalidPasswordException, rexc.base.UserNotFoundException:
        pass
    log('rejected auth for %s' %(username,))
    sys.stdout.write('false')

def doMetaData(data):
    log('meta %s' % (json.dumps(data),))
    if 'userid' not in data or data['userid'] == 'none':
        print 'no userid'
        return
    user = User.get_user(id=data['userid'])
    if user == None:
        print 'user not found'
        return
    artist = data['artist'] or ''
    title = data['title'] or ''
    if 'song' in data:
        song = data['song'].split(' - ', 1)
        if ('artist' not in data) or (len(data['artist'].strip()) == 0):
            artist = song[0]
        if ('title' not in data) or (len(data['title'].strip()) == 0):
            title = song[1]
    if user.get_setting(code='use_icy'):
        if 'ice-genre' in data:
            tags = data['ice-genre']
        if 'ice-name' in data:
            name = data['ice-name']
        if 'ice-description' in data:
            description = data['ice-decription']
    else:
        tags = user.get_setting(code='show_def_tags')
        description = user.get_setting(code='show_def_desc')
        name = user.get_setting(code='show_def_name')
    show = init_show(user, name=name, description=description, tags=tags)
    track = Track.new_track(show, artist, title)
    rfk.database.session.add(track)
    rfk.database.session.commit()

def doConnect(data):
    """handles a connect from liquidsoap
    
    Keyword arguments:
    data -- list of headers
    
    """
    log('auth request %s' % (json.dumps(data),))
    auth = data['Authorization'].strip().split(' ')
    if auth[0].lower() == 'basic':
        a = base64.b64decode(auth[1]).split(':', 1)
        if a[0] == 'source':
            a = a[1].split(username_delimiter, 1)
        username = a[0]
        password = a[1]
    else:
        kick()
        return 
    try:
        user = User.authenticate(username, password)
        if user.get_setting(code='use_icy'):
            if 'ice-genre' in data:
                tags = data['ice-genre']
            if 'ice-name' in data:
                name = data['ice-name']
            if 'ice-description' in data:
                description = data['ice-decription']
        else:
            tags = user.get_setting(code='show_def_tags')
            description = user.get_setting(code='show_def_desc')
            name = user.get_setting(code='show_def_name')
        show = init_show(user, name=name, description=description, tags=tags)
        rfk.database.session.commit()
        log('accepted auth for %s' %(user.username,))
        print user.user
    except rexc.base.InvalidPasswordException, rexc.base.UserNotFoundException:
        log('rejected auth for %s' %(username,))
        kick()

def doDisconnect(userid):
    if userid == "none":
        print "Whooops no userid?"
        return
    
    user = User.get_user(id=int(userid))
    if user:
        usershows = UserShow.query.filter(UserShow.user == user,
                                          UserShow.status == UserShow.STATUS.STREAMING).all()
        for usershow in usershows:
            usershow.status = UserShow.STATUS.STREAMED
            if usershow.show.flags & Show.FLAGS.UNPLANNED:
                usershow.show.end_show()
        rfk.database.session.commit()
    else:
        print "no user found"

def doPlaylist():
    #item = rfk.Playlist.getCurrentItem(session)
    print os.path.join(basedir, 'var', 'music', 'loop.mp3')

def doListenerCount():
    lc = Listener.get_total_listener()
    sys.stdout.write("<icestats><source mount=\"/live.ogg\"><listeners>%d</listeners></source></icestats>" % (lc,))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyRfK Interface for liquidsoap',
                                     epilog='Anyways this should normally not called manually')
    parser.add_argument('--debug', action='store_true')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    
    authparser = subparsers.add_parser('auth', help='a help')
    authparser.add_argument('username')
    authparser.add_argument('password')
    
    metadataparser = subparsers.add_parser('meta', help='a help')
    metadataparser.add_argument('data', metavar='data', help='mostly some json encoded string from liquidsoap')
    connectparser = subparsers.add_parser('connect', help='a help')
    connectparser.add_argument('data', metavar='data', help='mostly some json encoded string from liquidsoap')
    disconnectparser = subparsers.add_parser('disconnect', help='a help')
    disconnectparser.add_argument('data', metavar='data', help='mostly some json encoded string from liquidsoap')
    playlistparser = subparsers.add_parser('playlist', help='a help')
    playlistparser = subparsers.add_parser('listenercount', help='prints total listenercount')
    
    args = parser.parse_args()
    
    rfk.init(basedir)
    rfk.database.init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                              rfk.CONFIG.get('database', 'username'),
                                                              rfk.CONFIG.get('database', 'password'),
                                                              rfk.CONFIG.get('database', 'host'),
                                                              rfk.CONFIG.get('database', 'database')))
    if args.command == 'auth':
        doAuth(args.username, args.password)
    elif args.command == 'meta':
        data = json.loads(args.data);
        doMetaData(data)
    elif args.command == 'connect':
        data = json.loads(args.data);
        doConnect(data)
    elif args.command == 'disconnect':
        data = json.loads(args.data);
        doDisconnect(data)
    elif args.command == 'playlist':
        doPlaylist()
    elif args.command == 'listenercount':
        doListenerCount()
    rfk.database.session.remove()