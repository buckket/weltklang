import cherrypy
import auth
import rfk
from rfk.api import API
from user import User
import os
import postmarkup

class Site(object):
    '''
    classdocs
    '''
    
    login = auth.AuthController()
    api   = API()
    user = User()
    
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
        