import cherrypy
from rfk.api.icecast import IcecastAPI
class API(object):
    
    icecast = IcecastAPI()
    @cherrypy.expose
    def index(self):
        
        return 'apiindex'
    
    