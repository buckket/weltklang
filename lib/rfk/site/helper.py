'''
Created on 14.05.2012

@author: teddydestodes
'''

from rfk.database.track import Track
import postmarkup
import datetime
from flaskext.babel import format_time
from flask import request

def nowPlaying():
    track = Track.current_track()
    if track:
        title = "%s - %s" % (track.title.artist.name,track.title.name)
        users = []
        for usershow in track.show.users:
            users.append(usershow)
        return {
                'title': title,
                'users': users,
                'showname': track.show.name,
                'showdescription':track.show.description
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