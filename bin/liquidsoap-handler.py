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
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))

def doAuth(username,password,session):
    user = session.query(rfk.User).filter(rfk.User.name == username).first();
    if user != None and user.checkStreamPassword(password):
        print 'true'
    else:
        print 'false'

def doMetaData(data,session):
    pass

def doConnect(data,session):
    auth = data.Authorization.strip().split(' ')
    if auth[0].lower() == 'basic':
        a = auth[1].split(':',1)
        if a[0] == 'source':
            a = a[1].split(':',1)
        username = a[0]
        password = a[1]
    
    user = session.query(rfk.User).filter(rfk.User.name == username).first();
    if user != None and user.checkPassword(password):
        shows = rfk.Show.getCurrentShow(session, user)
        if len(shows) == 0:
            show = rfk.Show()
            session.add(Show)
            session.commit()
        else:
            for show in shows:
                pass
        print 'true'

def doDisconnect(data,session):
    pass

def doPlaylist(session):
    item = rfk.Playlist.getCurrentItem(session)
    print os.path.join(current_dir,'var','music',item.file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyRfK Interface for liquidsoap',
                                     epilog='Anyways this should normally not called manually')
    parser.add_argument('--debug',action='store_true')
    subparsers = parser.add_subparsers(dest='command',help='sub-command help')
    
    authparser = subparsers.add_parser('auth', help='a help')
    authparser.add_argument('username')
    authparser.add_argument('password')
    
    metadataparser = subparsers.add_parser('metadata', help='a help')
    metadataparser.add_argument('data',metavar='data', help='mostly some json encoded string from liquidsoap')
    connectparser = subparsers.add_parser('connect', help='a help')
    connectparser.add_argument('data',metavar='data', help='mostly some json encoded string from liquidsoap')
    disconnectparser = subparsers.add_parser('disconnect', help='a help')
    disconnectparser.add_argument('data',metavar='data', help='mostly some json encoded string from liquidsoap')
    playlistparser = subparsers.add_parser('playlist', help='a help')
    
    args = parser.parse_args()
    engine = create_engine("%s://%s:%s@%s/%s?charset=utf8" % (rfk.config.get('database', 'engine'),
                                                              rfk.config.get('database', 'username'),
                                                              rfk.config.get('database', 'password'),
                                                              rfk.config.get('database', 'host'),
                                                              rfk.config.get('database', 'database')))
    Session = sessionmaker(bind=engine)
    session = Session()
    if args.command == 'auth':
        doAuth(args.username,args.password,session)
    elif args.command == 'metadata':
        data = json.loads(args.data);
        doMetaData(data,session)
    elif args.command == 'connect':
        data = json.loads(args.data);
        doConnect(data,session)
    elif args.command == 'disconnect':
        data = json.loads(args.data);
        doDisconnect(data,session)
    elif args.command == 'playlist':
        doPlaylist(session)
    session.close()