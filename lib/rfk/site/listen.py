'''
Created on 13.05.2012

@author: teddydestodes
'''
import rfk
from flask import Blueprint, make_response
from rfk.database.streaming import Stream, Relay
from flask.templating import render_template
listen = Blueprint('listen',__name__)

@listen.route('/')
def html5_player():
    return render_template('html5player.html')

@listen.route('/<stream>')
def playlist(stream):
    stream = Stream.query.filter(Stream.code == stream).first()
    m3u  = "#EXTM3U\r\n"
    m3u += "#EXTINF:0, Radio freies Krautchan %s\r\n" % stream.name
    m3u += "http://%s/listen/stream/%s\r\n" % (rfk.CONFIG.get('site', 'url'), stream.stream)
    return make_response(m3u, 200, {'Content-Type': 'audio/x-mpegurl','Content-Disposition':'attachment; filename="%s.m3u"' % stream.mount[1:]})

@listen.route('/stream/<stream>')
def stream(stream):
    """
    redirect listener to best relay
    @todo loadbalancing
    """
    stream = Stream.query.get(int(stream))
    relay = Relay.query.first()
    #@hack DO NOT COMMIT
    if relay.address == '192.168.122.156':
        address = 'rfkbeta.0xfefe.org'
    else:
        address = relay.address
    return make_response('', 301, {'Location':"http://%s:%s%s" % (address, relay.port, stream.mount), 'X-LOAD':0})
