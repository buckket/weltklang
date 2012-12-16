'''
Created on 04.05.2012

@author: teddydestodes
'''
import rfk
import rfk.database
from rfk.database.base import User, Permission, UserPermission
from rfk.database.streaming import Stream, Relay, StreamRelay
import os

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.init(current_dir)
    rfk.database.init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                              rfk.CONFIG.get('database', 'username'),
                                                              rfk.CONFIG.get('database', 'password'),
                                                              rfk.CONFIG.get('database', 'host'),
                                                              rfk.CONFIG.get('database', 'database')))
    
    stream = Stream()
    stream.mount = '/radio.ogg'
    stream.code = 'ogg'
    stream.type = Stream.TYPES.OGG
    stream.quality = 3
    #rfk.database.session.add(stream)
    #rfk.database.session.commit()
    relay = Relay()
    relay.address = '192.168.122.73'
    relay.type = Relay.TYPE.RELAY
    relay.status = Relay.STATUS.UNKNOWN
    relay.port = 8000
    relay.admin_username = 'admin'
    relay.admin_password = 'entengruetze'
    relay.auth_username = 'master'
    relay.auth_password = 'master'
    #relay.relay_password = 'radiowegrelayen'
    #relay.relay_username = 'relay'
    #rfk.database.session.add(relay)
    #rfk.database.session.commit()
    relay = Relay.get_relay(address=relay.address, port=relay.port)
    relay.add_stream(Stream.query.first())
    print relay.get_icecast_config()
    rfk.database.session.commit()