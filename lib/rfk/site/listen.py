'''
Created on 13.05.2012

@author: teddydestodes
'''
import cherrypy
import rfk


class Listen(object):
    '''
    stream loadbalancer
    '''
    
    @cherrypy.expose
    def index(self, stream):
        stream = cherrypy.request.db.query(rfk.Stream).get(int(stream))
        cherrypy.response.headers['Content-Type'] = 'audio/x-mpegurl';
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="rfk.m3u"';
        response  = "#EXTM3U\r\n";
        response += "#EXTINF:0, Radio freies Krautchan %s\r\n" % stream.description;
        response += "http://%s/listen/%s\r\n" % (rfk.config.get('site', 'url'), stream);
        return response
    
    @cherrypy.expose
    def stream(self, stream):
        """
        redirect listener to best relay
        """
        stream = cherrypy.request.db.query(rfk.Stream).get(int(stream))
        relay = rfk.Relay.getBestRelay(cherrypy.request.db)
        cherrypy.response.headers['Location'] = stream.getURL(relay)
        cherrypy.response.headers['X-LOAD'] = relay.getLoad()
        return ''
