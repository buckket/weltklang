import datetime
from functools import wraps, partial
import math

import postmarkup
import humanize

import rfk
from rfk.database.track import Track
from flask.ext.babel import format_time, get_locale
from flask import request, url_for, jsonify
from flask.ext.login import current_user
from rfk.database.show import Show
from flask_babel import to_user_timezone, to_utc
from rfk.helper import now, iso_country_to_countryball, make_user_link, natural_join
from rfk.database.streaming import Listener


# Jinja 2 global: piwik_url
def piwik_url():
    if rfk.CONFIG.has_option('site', 'piwik-url'):
        return rfk.CONFIG.get('site', 'piwik-url')
    else:
        return None

# Jinja2 global: get_disco
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

# Jinja2 global: now_playing
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
markup.tag_factory.set_default_tag(postmarkup.DefaultTag)


# Jinja2 filter: bbcode
def bbcode(value):
    return markup.render_to_html(value, render_unknown_tags=True)


# Jinja2 filter: timedelta
def timedelta(value):
    days = value.days
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return u"{days} Days, {hours} Hours, {minutes} Minutes and {seconds} Seconds".format(days=days,
                                                                                         hours=hours,
                                                                                         minutes=minutes,
                                                                                         seconds=seconds)
    # WTF!? <- Double return? WTF, indeed.
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


# Pagination helper


def paginate_query(query, page=0, per_page=25):
    result = query.limit(per_page).offset((page - 1) * per_page).all()
    total_count = query.count()
    return (result, total_count)


# Jinja2 global: url_for_other_page
def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(math.ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
                num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def naturaltime(dt):
    # i18n isnt working because of various fuckups
    # will fix later

    #locale = get_locale()
    #locale_name = '_'.join([locale.language, locale.territory])
    #humanize.i18n.activate(locale_name)

    return humanize.time.naturaltime(now() - dt)


def naturaldelta(dt):
    return humanize.time.naturaldelta(dt)
