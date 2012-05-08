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

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyRfK Interface for liquidsoap',
                                     epilog='Anyways this should normally not called manually')
    parser.add_argument('--debug')
    parser.add_argument('command',metavar='command',choices=['auth','metadata','connect','disconnect'],
                        help='command to execute')
    parser.add_argument('data',metavar='data', help='mostly some json encoded string from liquidsoap')
    args = parser.parse_args()
    data = json.loads(args.data);
    engine = create_engine("%s://%s:%s@%s/%s?charset=utf8" % (rfk.config.get('database', 'engine'),
                                                              rfk.config.get('database', 'username'),
                                                              rfk.config.get('database', 'password'),
                                                              rfk.config.get('database', 'host'),
                                                              rfk.config.get('database', 'database')))
    Session = sessionmaker(bind=engine)
    session = Session()
    if data.command == 'auth':
        doAuth(data,session)
    elif data.command == 'metadata':
        doMetaData(data,session)
    elif data.command == 'connect':
        doConnect(data,session)
    elif data.command == 'disconnect':
        doDisconnect(data,session)
    session.close()
    
def doAuth(data,session):
    user = session.query(rfk.User).filter(rfk.User.name == data.username).first();
    if user != None and user.checkPassword(data.password):
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