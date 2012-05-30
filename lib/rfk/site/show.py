'''
Created on 16.05.2012

@author: teddydestodes
'''

import cherrypy
import postmarkup
import rfk
class Show(object):
    '''
    classdocs
    '''

    @cherrypy.expose
    @cherrypy.tools.jinja(template='index.html')
    def index(self):
        nq = cherrypy.request.db.query(rfk.News).order_by(rfk.News.time.desc()).all()
        
        news = []
        markup = postmarkup.PostMarkup()
        markup.default_tags()
        
        for n in nq:
            news.append({'time':n.time,
                         'title': markup.render_to_html(n.title),
                         'content': markup.render_to_html(n.content)})
        
        return {'news':news}
    
    def __init__(self):
        '''
        Constructor
        '''