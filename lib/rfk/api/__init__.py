import cherrypy
from rfk.api.icecast import IcecastAPI
from rfk.api.webapi import WebAPI

class API(object):
    
    icecast = IcecastAPI()
    web = WebAPI()
    
    @cherrypy.expose
    def index(self):
        
        return 'apiindex'
    
    