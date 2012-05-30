'''
Created on 16.05.2012

@author: teddydestodes
'''


import cherrypy
import rfk
from datetime import datetime

class Shows(object):
    '''
    classdocs
    '''

    @cherrypy.expose
    @cherrypy.tools.jinja(template='calendar.html')
    def calendar(self):
        pass

    def __init__(self):
        '''
        Constructor
        '''