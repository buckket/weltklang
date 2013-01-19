'''
Created on 14.05.2012

@author: teddydestodes
'''

import rfk.site
import rfk
import postmarkup
import datetime
from flaskext.babel import format_time
from flask import request

def nowPlaying():
    song = rfk.site.db.session.query(rfk.Song).filter(rfk.Song.end == None).first()
    if song:
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
    else:
        return None

def menu():
    return request.menu

markup = postmarkup.PostMarkup()
markup.default_tags()
def bbcode(value):
    return markup.render_to_html(value)

def timedelta(value):
    days = value.days
    hours, remainder = divmod(value.seconds,3600)
    minutes, seconds = divmod(remainder,60)
    return u"{days} Days, {hours} Hours, {minutes} Minutes and {seconds} Seconds".format(days=days,
                                                                                         hours=hours,
                                                                                         minutes=minutes,
                                                                                         seconds=seconds)

    return format_time((datetime.datetime.min + value).time())