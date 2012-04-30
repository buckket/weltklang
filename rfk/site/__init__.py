import cherrypy
import auth
import os
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader(os.path.join('var','templates','rfk')))

class Site(object):
    '''
    classdocs
    '''
    
    login = auth.AuthController()
    
    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('index.html')
        return tmpl.render()
    
    def __init__(self):
        '''
        Constructor
        '''
        