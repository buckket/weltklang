import cherrypy
from rfk.api.icecast import Icecast
class API(object):
    
    icecast = Icecast()
    @cherrypy.expose
    def index(self):
        
        return 'apiindex'
    
    