from flask import Blueprint, make_response
from flask.templating import render_template

import rfk
from rfk.database.streaming import Stream


listen = Blueprint('listen', __name__)


@listen.route('/')
def html5_player():
    return render_template('html5player.html')


@listen.route('/<stream>')
def playlist(stream):
    """Return a m3u playlist pointing to our load balancer"""

    stream = Stream.query.filter(Stream.code == stream).first()
    if stream is None:
        return make_response('I\'m sorry ;_; (Invalid stream)', 404)
    m3u = "#EXTM3U\r\n"
    m3u += "#EXTINF:0, Radio freies Krautchan %s\r\n" % stream.name
    m3u += "http://%s/listen/stream/%s\r\n" % (rfk.CONFIG.get('site', 'url'), stream.stream)
    return make_response(m3u, 200, {'Content-Type': 'application/x-mpegurl',
                                    'Content-Disposition': 'attachment; filename="%s.m3u"' % stream.mount[1:]})


@listen.route('/stream/<stream>')
def stream(stream):
    """Redirect listener to relay with least traffic usage"""

    stream = Stream.query.get(int(stream))
    if stream is None:
        return make_response('I\'m sorry ;_; (Invalid stream)', 404)

    relay = stream.get_relay()
    if relay is None:
        return make_response('I\'m sorry ;_; (No suitable relays found)', 503)

    address = relay.address
    return make_response('', 301, {'Location': "http://%s:%s%s" % (address, relay.port, stream.mount), 'X-LOAD': round(relay.get_load(), 2)})
