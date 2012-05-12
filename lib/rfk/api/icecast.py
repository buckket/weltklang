'''
Created on 09.05.2012

@author: teddydestodes
'''
import cherrypy
import rfk
from datetime import datetime
class IcecastAPI(object):
    '''
    Icecast HTTPAPI
    '''
    @cherrypy.expose
    def index(self, **data):
        print data
        server = data['server']
        mount = data['mount']
        action = data['action']
        ip = data['ip']
        mount = cherrypy.request.db.query(rfk.Stream).filter(rfk.Stream.mountpoint == mount).first()
        if mount == None:
            cherrypy.response.headers['icecast-auth-message'] = 'unknown mountpoint'
            print 'unknown mountpoint'
            return 'unknown mountpoint'
        
        relay = cherrypy.request.db.query(rfk.Relay).filter(rfk.Relay.hostname == server).first()
        if relay == None:
            if action == 'mount_add':
                # we assume port 8000 here sinde it's the standardport for icecast
                relay = rfk.Relay(hostname=server, port=8000, name=server)
                mount.relays.append(relay)
                cherrypy.request.db.add(relay)
            else:
                cherrypy.response.headers['icecast-auth-message'] = 'unknown or not registered server'
            print 'unknown or not registered server'
            return 'unknown or not registered server'
        
        if action in ['mount_add', 'listener_add', 'listener_remove']:
            relay.status = rfk.Relay.STATUS_ONLINE
        if action == 'stream_auth':
            user = data['user']
            password = data['pass']
        elif action == 'listener_add':
            #@todo: icecast need to be filtered
            # something like /^Icecast/
            agent = data['agent']
            client = data['client']
            listener = rfk.Listener(connect=datetime.today(), address=ip, client=client, useragent=agent, relay=relay, stream=mount)
            cherrypy.request.db.add(listener)
        elif action == 'listener_remove':
            client = data['client']
            rfk.Listener.setDisconnected(cherrypy.request.db, relay, mount, client)
        elif action == 'mount_add':
            mount.add(cherrypy.request.db, relay)
        elif action == 'mount_remove':
            mount.remove(cherrypy.request.db, relay)
        
        cherrypy.request.db.commit()
        cherrypy.response.headers['icecast-auth-user'] = '1'
        return 'ok'

    def __init__(self):
        '''
        go ahead, nothing to see here
        '''
        
        
