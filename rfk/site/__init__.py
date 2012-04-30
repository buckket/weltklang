import cherrypy
import auth
from rfk.api import API
import os
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.path.join('var','templates','rfk')))

class Site(object):
    '''
    classdocs
    '''
    
    login = auth.AuthController()
    api   = API()
    
    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('index.html')
        return tmpl.render()
    
    @cherrypy.expose
    def loom(self,param=None):
        return 'loom ist ein pups %s' % param
    
    def __init__(self):
        '''
        Constructor
        '''
        