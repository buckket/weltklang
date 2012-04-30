import cherrypy

class API(object):
    
    @cherrypy.expose
    def index(self):
        return 'apiindex'
    
    