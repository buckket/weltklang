'''
Created on 13.05.2012

@author: teddydestodes
'''
import rfk
from flask import Blueprint, make_response
from rfk.site import db
listen = Blueprint('listen',__name__)

@listen.route('/playlist/<stream>')
def playlist(stream):
    stream = db.session.query(rfk.Stream).filter(rfk.Stream.name == stream).first()
    m3u  = "#EXTM3U\r\n";
    m3u += "#EXTINF:0, Radio freies Krautchan %s\r\n" % stream.description;
    m3u += "http://%s/listen/%s\r\n" % (rfk.config.get('site', 'url'), stream);
    return make_response(m3u, 200, {'Content-Type': 'audio/x-mpegurl','Content-Disposition':'attachment; filename="%s.m3u"' % stream.mountpoint[1:]})

@listen.route('/stream/<stream>')
def stream(stream):
    """
    redirect listener to best relay
    """
    stream = db.session.query(rfk.Stream).get(int(stream))
    relay = rfk.Relay.get_best_relay(db.session)
    return make_response('', 301, {'Location':stream.get_url(relay), 'X-LOAD':relay.get_load()})
