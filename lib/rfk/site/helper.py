import datetime
from functools import wraps, partial
import math

import postmarkup

from rfk.database.track import Track
from flask.ext.babel import format_time
from flask import request, url_for, jsonify
from flask.ext.login import current_user


def nowPlaying():
    track = Track.current_track()
    if track:
        title = "%s - %s" % (track.title.artist.name, track.title.name)
        users = []
        for usershow in track.show.users:
            users.append(usershow)
        return {
            'title': title,
            'users': users,
            'showname': track.show.name,
            'showdescription': track.show.description
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
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return u"{days} Days, {hours} Hours, {minutes} Minutes and {seconds} Seconds".format(days=days,
                                                                                         hours=hours,
                                                                                         minutes=minutes,
                                                                                         seconds=seconds)
    # WTF!?
    return format_time((datetime.datetime.min + value).time())


def permission_required(f=None, permission=None, ajax=False):
    if f is None:
        return partial(permission_required, permission=permission, ajax=ajax)

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated():
            if ajax:
                return emit_error(0, 'Not Logged In!')
            else:
                return 'not logged in'
        if permission is not None and not current_user.has_permission(permission):
            if ajax:
                return emit_error(0, 'insufficient permissions')
            else:
                return 'insufficient permissions'
        return f(*args, **kwargs)

    return decorated_function


def emit_error(err_id, err_msg):
    return jsonify({'success': False, 'error': {'id': err_id, 'msg': err_msg}})


def paginate(query, page=0, per_page=25):
    result = query.limit(per_page).offset(page * per_page).all()
    total_pages = int(math.ceil(query.count() / per_page))
    return (result, total_pages)


def pagelinks(url, page, total_pages, visible_pages=7, param='page'):
    pagelinks = {'first': None,
                 'last': None,
                 'pages': []}
    if page > 0:
        pagelinks['first'] = url_for(url, **{param: 0})
    if page < total_pages:
        pagelinks['last'] = url_for(url, **{param: total_pages})
    begin = int(page - (visible_pages / 2))

    if begin + visible_pages > total_pages + 1:
        begin = total_pages + 1 - visible_pages
    if begin < 0:
        begin = 0
    end = min(begin + visible_pages, total_pages + 1)
    for pn in range(begin, end):
        pagelinks['pages'].append({'name': pn + 1,
                                   'active': pn == page,
                                   'url': url_for(url, **{param: pn})})
    return pagelinks
