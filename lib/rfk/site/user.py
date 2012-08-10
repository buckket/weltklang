'''
Created on 16.05.2012

@author: teddydestodes
'''


import cherrypy
import rfk
from datetime import datetime
class User(object):
    '''
    classdocs
    '''

    @cherrypy.expose
    @cherrypy.tools.jinja(template='user.html')
    def default(self, user):
        user = cherrypy.request.db.query(rfk.User).filter(rfk.User.name == user).first()
        if user:
            
            out = {}
            out['username'] = user.name
            out['info'] = {'totaltime': user.getStreamTime(cherrypy.request.db)[1]}
            ushows = cherrypy.request.db.query(rfk.Show).join(rfk.user_shows).join(rfk.User).filter(rfk.User.user==user.user, rfk.Show.begin > datetime.today()).order_by(rfk.Show.begin.asc())[:5]
            lshows = cherrypy.request.db.query(rfk.Show).join(rfk.user_shows).join(rfk.User).filter(rfk.User.user==user.user, rfk.Show.end <= datetime.today()).order_by(rfk.Show.end.desc())[:5]
            
            out['shows'] = {'upcomming': ushows,
                            'last': lshows
                            }
            
            
            return out
        else:
            return {'undefined':True}

    def __init__(self):
        '''
        Constructor
        '''