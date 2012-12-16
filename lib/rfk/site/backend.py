'''
Created on Aug 11, 2012

@author: teddydestodes
'''

from flask import Blueprint, render_template, g, request, make_response
import logging
from rfk.database.streaming import Relay, Stream, StreamRelay
from rfk.database import session


log = logging.getLogger('werkzeug')

backend = Blueprint('icecast',__name__)

@backend.route('/icecast/auth', methods=['POST'])
def icecast_auth():
    log.warning(request.form)
    if request.form['action'] != 'stream_auth':
        return make_response('you just went full retard', 405)
    relay = Relay.get_relay(address=request.form['server'],
                            port=request.form['port'])
    if relay.auth_password == request.form['pass'] and\
       relay.auth_username == request.form['user']:
        return make_response('ok', 200, {'icecast-auth-user': '1'})
    else:
        return make_response('authentication failed', 401)
    
@backend.route('/icecast/add', methods=['POST'])
def icecast_add_mount():
    log.warning(request.form)
    if request.form['action'] != 'mount_add':
        return make_response('you just went full retard', 405)
    relay = Relay.get_relay(address=request.form['server'],
                            port=request.form['port'])
    stream = Stream.get_stream(mount=request.form['mount'])
    if relay and stream:
        stream.add_relay(relay)
        relay.get_stream_relay(stream).status = StreamRelay.STATUS.ONLINE
        session.commit()
        return make_response('ok', 200, {'icecast-auth-user': '1'})
    else:
        return make_response('something strange happened', 500)
    
@backend.route('/icecast/remove', methods=['POST'])
def icecast_remove_mount():
    log.warning(request.form)
    if request.form['action'] != 'mount_remove':
        return make_response('you just went full retard', 405)
    relay = Relay.get_relay(address=request.form['server'],
                            port=request.form['port'])
    stream = Stream.get_stream(mount=request.form['mount'])
    if relay and stream:
        stream.add_relay(relay)
        relay.get_stream_relay(stream).status = StreamRelay.STATUS.OFFLINE
        session.commit()
        return make_response('ok', 200, {'icecast-auth-user': '1'})
    else:
        return make_response('something strange happened', 500)

@backend.route('/icecast/listenerremove', methods=['POST'])
def icecast_remove_listener():
    log.warning(request.form)
    return make_response('something strange happened', 500)

@backend.route('/icecast/listeneradd', methods=['POST'])
def icecast_add_listener():
    log.warning(request.form)
    return make_response('something strange happened', 500)