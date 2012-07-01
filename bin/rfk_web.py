#!/usr/bin/python
'''
Created on 30.04.2012

@author: teddydestodes
'''
import cherrypy
import os
import rfk
from rfk.tools.jinjaloader import JinjaLoader, JinjaHandler
from rfk.tools import SAEnginePlugin, SATool

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    
    
    rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))
    
    cherrypy.config.update({'environment': 'test_suite',
                            'log.error_file': os.path.join(current_dir, 'var','log','site.log'),
                            'log.screen': True,
                            'tools.sessions.on': True,
                            'tools.auth.on': True,
                            'server.socket_host': rfk.config.get('site', 'listen'),
                            'server.socket_port': rfk.config.getint('site', 'port')
                            
                            })
    
    conf = {'/'      : {'tools.db.on': True,
                        'tools.jinja.on': True,
             },
            '/api' :{'tools.jinja.on': False,
                     },
            '/static': {'tools.staticdir.on': True,
                        'tools.jinja.on': False,
                        'tools.staticdir.dir': os.path.join(current_dir, 'web_static'),
                        'tools.staticdir.content_types': {'rss': 'application/xml',
                                                          'atom': 'application/atom+xml'}},
            '/favicon.ico': {'tools.staticfile.on': True,
                             'tools.jinja.on': False,  
                             'tools.staticfile.filename': '/web_static/favicon.ico',  
            }}
    
    loader = JinjaLoader(os.path.join(current_dir,'var','template'))#
    
    cherrypy.tools.jinja = cherrypy.Tool('before_handler', loader, priority=70)
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()
    import rfk.site
    import rfk.site.helper
    loader.add_global(rfk.site.helper.nowPlaying)
    loader.add_filter(rfk.site.helper.bbcode)
    loader.add_filter(rfk.site.helper.timedelta)
    cherrypy.tree.mount(rfk.site.Site(), '/', config=conf)
    cherrypy.engine.start()
    cherrypy.engine.block()