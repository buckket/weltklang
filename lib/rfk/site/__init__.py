import cherrypy
import auth
import rfk
from rfk.api import API
import os


class Site(object):
    '''
    classdocs
    '''
    
    login = auth.AuthController()
    api   = API()
    
    @cherrypy.expose
    def index(self):
        tmpl = rfk.env.get_template('index.html')
        return tmpl.render()
    
    @cherrypy.expose
    def loom(self,param=None):
        return 'loom ist ein pups %s' % param
    
    def __init__(self):
        '''
        Constructor
        '''
        