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
    def index(self, server=None, mount=None, action=None, ip=None, client=None, agent=None):
        cherrypy.log().error("peh: %s %s %s %s %s %s" % (server,mount,action, ip, client, agent))
        mount = cherrypy.request.db.query(rfk.Stream).filter(rfk.Stream.mountpoint == mount).first()
        if mount == None:
            cherrypy.response.headers['icecast-auth-message'] = 'unknown mountpoint'
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
            return 'unknown or not registered server'
        
        if action in ['mount_add', 'listener_add', 'listener_remove']:
            relay.status = rfk.Relay.STATUS_ONLINE
        
        if action == 'listener_add':
            #@todo: icecast need to be filtered
            # something like /^Icecast/
            listener = rfk.Listener(connect=datetime.today(), address=ip, client=client, useragent=agent, relay=relay, mount=mount)
            cherrypy.request.db.add(listener)
        elif action == 'listener_remove':
            rfk.Listener.setDisconnected(cherrypy.response.db, relay, mount, client)
        elif action == 'mount_add':
            mount.add(cherrypy.response.db, relay)
        elif action == 'mount_remove':
            mount.disconnect(cherrypy.response.db, relay)
        cherrypy.response.db.commit()
        cherrypy.response.headers['icecast-auth-user'] = '1'
        

    def __init__(self):
        '''
        go ahead, nothing to see here
        '''
        
        
