'''
Created on 09.05.2012

@author: teddydestodes
'''
import rfk
from rfk.site import db
from rfk.api import api
from flask import request, make_response
from datetime import datetime

'''
Icecast HTTPAPI
'''
    
@api.route('/icecast/', methods=['POST'])
def index():
    
    server = request.form['server']
    mount = request.form['mount']
    action = request.form['action']
    ip = request.form['ip']

    mount = db.session.query(rfk.Stream).filter(rfk.Stream.mountpoint == mount).first()
    if mount == None:
        #cherrypy.response.headers['icecast-auth-message'] = 'unknown mountpoint'
        print 'unknown mountpoint'
        return make_response('unknown mountpoint', 400, {'icecast-auth-message': 'unknown mountpoint'})
    
    relay = db.session.query(rfk.Relay).filter(rfk.Relay.hostname == server).first()
    if relay == None:
        if action == 'mount_add':
            # we assume port 8000 here sinde it's the standardport for icecast
            relay = rfk.Relay(hostname=server, port=8000, name=server)
            mount.relays.append(relay)
            db.session.add(relay)
        else:
            #cherrypy.response.headers['icecast-auth-message'] = 'unknown or not registered server'
            print 'unknown or not registered server'
            return make_response('unknown or not registered server', 400, {'icecast-auth-message': 'unknown or not registered server'})
    
    if action in ['mount_add', 'listener_add', 'listener_remove']:
        relay.status = rfk.Relay.STATUS_ONLINE
    if action == 'stream_auth':
        user = request.form['user']
        password = request.form['pass']
    elif action == 'listener_add':
        #@todo: icecast need to be filtered
        # something like /^Icecast/
        agent = request.form['agent']
        client = request.form['client']
        listener = rfk.Listener(connect=datetime.today(), address=ip, client=client, useragent=agent, relay=relay, stream=mount)
        db.session.add(listener)
    elif action == 'listener_remove':
        client = request.form['client']
        rfk.Listener.set_disconnected(db, relay, mount, client)
    elif action == 'mount_add':
        mount.add(db, relay)
    elif action == 'mount_remove':
        mount.remove(db, relay)
    
    db.session.commit()
    #cherrypy.response.headers['icecast-auth-user'] = '1'
    return make_response('ok', 200, {'icecast-auth-user': '1'})

def __init__(self):
    '''
    go ahead, nothing to see here
    '''
    
    