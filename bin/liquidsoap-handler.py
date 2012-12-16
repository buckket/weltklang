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
import rfk
import argparse
import json
import os
import sys
import base64
from datetime import datetime
from rfk.database import init_db, session


username_delimiter = '|'

def doAuth(username, password, session):
    if username == 'source':
        username, password = password.split(username_delimiter)
    user = session.query(rfk.User).filter(rfk.User.name == username).first();
    if user != None and user.checkStreamPassword(password):
        sys.stdout.write('true')
    else:
        sys.stdout.write('false')

def doMetaData(data, session):
    if 'userid' not in data or data['userid'] == 'none':
        print 'no userid'
        return
    user = session.query(rfk.User).get(int(data['userid']))
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
    shows = rfk.Show.getCurrentShows(session, user)
    currshow = None
    for show in shows:
        if currshow and show.end is None:
            print show.show
            show.end = datetime.today()
            break
        currshow = show
    song = rfk.Song.beginSong(session, datetime.today(), artist, title, currshow)
    session.add(song)
    session.commit()

def doConnect(data, session):
    auth = data['Authorization'].strip().split(' ')
    if auth[0].lower() == 'basic':
        a = base64.b64decode(auth[1]).split(':', 1)
        if a[0] == 'source':
            a = a[1].split(username_delimiter, 1)
        username = a[0]
        password = a[1]
    user = session.query(rfk.User).filter(rfk.User.name == username).first();
    if user != None and user.checkStreamPassword(password):
        shows = rfk.Show.getCurrentShows(session, user)
        if len(shows) == 0:
            show = rfk.Show(begin=datetime.today())
            session.add(show)
            show.users.append(user)
            if True:
                if 'ice-genre' in data:
                    show.updateTags(session, data['ice-genre'])
                if 'ice-name' in data:
                    show.name = data['ice-name']
                if 'ice-description' in data:
                    show.description = data['ice-description']
            session.commit()
        else:
            for show in shows:
                pass
        print user.user

def doDisconnect(userid, session):
    if userid == "none":
        print "Whooops no userid?"
        return
    
    user = session.query(rfk.User).get(int(userid))
    if user:
        shows = rfk.Show.getCurrentShows(session, user)
        for show in shows:
            show.endShow()
        session.commit()
    else:
        print "no user found"

def doPlaylist():
    #item = rfk.Playlist.getCurrentItem(session)
    print os.path.join(current_dir, 'var', 'music', 'loop.mp3')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyRfK Interface for liquidsoap',
                                     epilog='Anyways this should normally not called manually')
    parser.add_argument('--debug', action='store_true')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    
    authparser = subparsers.add_parser('auth', help='a help')
    authparser.add_argument('username')
    authparser.add_argument('password')
    
    metadataparser = subparsers.add_parser('metadata', help='a help')
    metadataparser.add_argument('data', metavar='data', help='mostly some json encoded string from liquidsoap')
    connectparser = subparsers.add_parser('connect', help='a help')
    connectparser.add_argument('data', metavar='data', help='mostly some json encoded string from liquidsoap')
    disconnectparser = subparsers.add_parser('disconnect', help='a help')
    disconnectparser.add_argument('data', metavar='data', help='mostly some json encoded string from liquidsoap')
    playlistparser = subparsers.add_parser('playlist', help='a help')
    
    args = parser.parse_args()
    
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.init(current_dir)
    init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                              rfk.CONFIG.get('database', 'username'),
                                                              rfk.CONFIG.get('database', 'password'),
                                                              rfk.CONFIG.get('database', 'host'),
                                                              rfk.CONFIG.get('database', 'database')))
    if args.command == 'auth':
        doAuth(args.username, args.password)
    elif args.command == 'metadata':
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
    #session.remove()