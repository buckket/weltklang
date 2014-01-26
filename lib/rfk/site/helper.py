import datetime
from functools import wraps, partial
import math

import postmarkup

from rfk.database.track import Track
from flask.ext.babel import format_time
from flask import request, url_for, jsonify
from flask.ext.login import current_user
from rfk.database.show import Show
from flask_babel import to_user_timezone
from rfk.helper import now, iso_country_to_countryball, make_user_link,\
    natural_join
from rfk.database.streaming import Listener

def disco():
    show = Show.get_active_show()
    ret = {}
    if show:
        user = show.get_active_user()
        ret['countryball'] = iso_country_to_countryball(user.country)
        ret['logo'] = show.get_logo(),
    else:
        ret['countryball'] = False
        ret['logo'] = False
    track = Track.current_track()
    if track:
        ret['track'] = {'title': track.title.name,
                        'artist': track.title.artist.name,
        }
            #get listenerinfo for disco
    listeners = Listener.get_current_listeners()
    ret['listener'] = {}
    for listener in listeners:
        ret['listener'][listener.listener] = {'listener': listener.listener,
                                              'county': listener.country,
                                              'countryball': iso_country_to_countryball(listener.country)}
    return ret

def now_playing():
    try:
        ret = {}
        #gather showinfos
        show = Show.get_active_show()
        if show:
            user = show.get_active_user()
            if show.end:
                end = int(to_user_timezone(show.end).strftime("%s")) * 1000
            else:
                end = None
            ret['show'] = {'id': show.show,
                           'name': show.name,
                           'begin': int(to_user_timezone(show.begin).strftime("%s")) * 1000,
                           'now': int(to_user_timezone(now()).strftime("%s")) * 1000,
                           'end': end,
                           'logo': show.get_logo(),
                           'type': Show.FLAGS.name(show.flags),
                           'user': {'countryball': iso_country_to_countryball(user.country)}
            }
            if show.series:
                ret['series'] = {'name': show.series.name}
            link_users = []
            for ushow in show.users:
                link_users.append(make_user_link(ushow.user))
            ret['users'] = {'links': natural_join(link_users)}


        #gather nextshow infos
        if show and show.end:
            filter_begin = show.end
        else:
            filter_begin = now()
        if request.args.get('full') == 'true':
            nextshow = Show.query.filter(Show.begin >= filter_begin).order_by(Show.begin.asc()).first();
            if nextshow:
                ret['nextshow'] = {'name': nextshow.name,
                                   'begin': int(to_user_timezone(nextshow.begin).strftime("%s")) * 1000,
                                   'logo': nextshow.get_logo()}
                if nextshow.series:
                    ret['nextshow']['series'] = nextshow.series.name
        return jsonify({'success': True, 'data': ret})
    except Exception as e:
        raise e
        return jsonify({'success': False, 'data': unicode(e)})


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
