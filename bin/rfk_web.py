#!/usr/bin/python2.7
'''
Created on 30.04.2012

@author: teddydestodes
'''
import cherrypy
import os
import rfk
from rfk.site import Site
from jinja2 import Environment, FileSystemLoader
from rfk.tools import SAEnginePlugin, SATool

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    
    
    rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))
    
    cherrypy.config.update({'environment': 'test_suite',
                            'log.error_file': os.path.join(current_dir, 'var','log','site.log'),
                            'log.screen': True,
                            'tools.sessions.on': True,
                            'tools.auth.on': True
                            })
    
    conf = {'/'      : {'tools.db.on': True,
             #           'tools.template.on': True
             },
            '/static': {'tools.staticdir.on': True,
                        'tools.staticdir.dir': os.path.join(current_dir, 'web_static'),
                        'tools.staticdir.content_types': {'rss': 'application/xml',
                                                          'atom': 'application/atom+xml'}},
            '/favicon.ico': {'tools.staticfile.on': True,  
                             'tools.staticfile.filename': '/web_static/favicon.ico',  
            }}
    

    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(Site(), '/', config=conf)
    cherrypy.engine.start()
    cherrypy.engine.block()