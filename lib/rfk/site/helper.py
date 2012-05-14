'''
Created on 14.05.2012

@author: teddydestodes
'''

import rfk
import cherrypy

def nowPlaying():
    song = cherrypy.request.db.query(rfk.Song).filter(rfk.Song.end == None).first()
    title = "%s - %s" % (song.title.artist.name,song.title.name)
    users = []
    for user in song.show.users:
        users.append(user.name)
    show = song.show
    return {
            'title': title,
            'users': users,
            'showname': show.name,
            'showdescription': show.description
            }