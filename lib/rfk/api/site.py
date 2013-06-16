from flask import jsonify, request, g
from flaskext.babel import to_user_timezone, to_utc, format_datetime
from flask_login import current_user
from sqlalchemy.sql.expression import between
from sqlalchemy import or_

import parsedatetime.parsedatetime as pdt
from time import mktime
from datetime import datetime, timedelta

from rfk.api import api
import rfk.database
from rfk.database.streaming import Stream
from rfk.database.show import Show, Series, Tag
from rfk.helper import now, natural_join
from rfk.site.helper import permission_required
from rfk.database.track import Track


def parse_datetimestring(datestring):
    cal = pdt.Calendar()
    return datetime.fromtimestamp(mktime(cal.parse(datestring)[0]))

@api.route("/site/listenergraphdata/<string:start>", methods=['GET'], defaults={'stop': 'now'})
@api.route("/site/listenergraphdata/<string:start>/<string:stop>", methods=['GET'])
def listenerdata(start,stop):
    from rfk.site import app
    app.logger.warn(start)
    app.logger.warn(stop)
    stop = parse_datetimestring(stop)
    start = parse_datetimestring(start)
    app.logger.warn(start)
    app.logger.warn(stop)
    ret = {'data':{}, 'shows':[]}
    
    streams = Stream.query.all()
    for stream in streams:
        ret['data'][str(stream.mount)] = []
        #just set an initial stating point from before the starting point
        stats = stream.statistic.get(stop=start, num=1, reverse=True)
        for stat in stats:
            c = stat.value
        else:
            c = 0
        ret['data'][str(stream.mount)].append((int(to_user_timezone(start).strftime("%s"))*1000,int(c)))
    
    #fill in the actual datapoints
    streams = Stream.query.all()
    for stream in streams:
        stats = stream.statistic.get(start=start, stop=stop)
        for stat in stats:
            ret['data'][str(stream.mount)].append((int(to_user_timezone(stat.timestamp).strftime("%s"))*1000,int(stat.value)))
    
    streams = Stream.query.all()
    for stream in streams:
        stats = stream.statistic.get(stop=stop, num=1, reverse=True)
        for stat in stats:
            c = stat.value
        else:
            c = 0
        ret['data'][str(stream.mount)].append((int(to_user_timezone(stop).strftime("%s"))*1000,int(c)))
        
    #get the shows for the graph
    shows = Show.query.filter(between(Show.begin, start, stop)\
                            | between(Show.end, start, stop)).order_by(Show.begin.asc()).all()
    for show in shows:
        ret['shows'].append({'name': show.name,
                             'b':int(to_user_timezone(show.begin).strftime("%s")),
                             'e':int(to_user_timezone(show.end).strftime("%s")),})
    return jsonify(ret)

@api.route('/site/series/query')
def series_query():
    series = Series.query.filter(Series.name.like('%%%s%%'%request.args.get('query')),or_(Series.public == True)).limit(10)
    ret = [];
    for s in series:
        ret.append({'id':s.series, 'name':s.name})
        
    return jsonify({'success':True, 'data':ret})

@api.route('/site/show/info')
def show_info():
    show = request.args.get('show')
    if show is None:
        return jsonify({'success':False, 'error':'no show set!'})
    
    show = Show.query.get(int(show))
    if show is None:
        return jsonify({'success':False, 'error':'no show found!'})
    ret = {'name': show.name, 'description': show.description,
           'begin': format_datetime(show.begin),
           #'duration': format_timedelta(show.end - show.begin,granularity='minute'),
           'users': []}
    for ushow in show.users:
        ret['users'].append({'username': ushow.user.username,
                             'status': ushow.status})
    return jsonify({'success':True, 'data':ret})

@api.route('/site/show/add', methods=['POST'])
@permission_required
def show_add():
    #from rfk.site import app
    #app.logger.warn(request.form)
    if 'begin' in request.form and\
       'description' in request.form and\
       'duration' in request.form and\
       'title' in request.form:
        if int(request.form['duration']) < 30:
            return jsonify({'success':False, 'error':'Duration to short'})
        if int(request.form['duration']) > 1440:
            return jsonify({'success':False, 'error':'Duration to long'})
        if len(request.form['title']) < 3:
            return jsonify({'success':False, 'error':'Title to short'})
        if len(request.form['description']) == 0:
            return jsonify({'success':False, 'error':'Description is empty'})
        begin = to_utc(datetime.fromtimestamp(int(request.form['begin'])))
        begin = begin.replace(second=0)
        if begin < now():
            return jsonify({'success':False, 'error':'You cannot enter a past date!'})
        end = begin+timedelta(minutes=int(request.form['duration']))
        if Show.query.filter(Show.end > begin , Show.begin < end).count() > 0:
            return jsonify({'success':False, 'error':'Your show collides with other shows'})
        show = Show(begin=begin,
                    end=end,
                    name=request.form['title'],
                    description=request.form['description'],
                    flags=Show.FLAGS.PLANNED)
        rfk.database.session.add(show)
        show.add_user(current_user)
        rfk.database.session.flush()
        if 'series' in request.form and\
           len(request.form['series']) > 0 and\
           int(request.form['series']) > 0:
            show.series_id = int(request.form['series'])
        if 'tags' in request.form and\
           len(request.form['tags']) > 0:
            tags = Tag.parse_tags(request.form['tags'].replace(',',' '))
            show.add_tags(tags)
        if 'logo' in request.form and\
           len(request.form['logo']) > 0:
            show.logo = request.form['logo']
        rfk.database.session.commit()
        
    return jsonify({'success':True, 'data':None})

@api.route('/site/show/<int:show>/edit', methods=['POST'])
def show_edit(show):
    #from rfk.site import app
    #app.logger.warn(request.form)
    if 'begin' in request.form and\
       'description' in request.form and\
       'duration' in request.form and\
       'title' in request.form:
        if int(request.form['duration']) < 30:
            return jsonify({'success':False, 'error':'Duration to short'})
        if int(request.form['duration']) > 1440:
            return jsonify({'success':False, 'error':'Duration to long'})
        if len(request.form['title']) < 3:
            return jsonify({'success':False, 'error':'Title to short'})
        if len(request.form['description']) == 0:
            return jsonify({'success':False, 'error':'Description is empty'})
        begin = to_utc(datetime.fromtimestamp(int(request.form['begin'])))
        begin = begin.replace(second=0)
        if begin < now():
            return jsonify({'success':False, 'error':'You cannot enter a past date!'})
        end = begin+timedelta(minutes=int(request.form['duration']))
        if Show.query.filter(Show.end > begin , Show.begin < end, Show.show != show).count() > 0:
            return jsonify({'success':False, 'error':'Your show collides with other shows'})
        show = Show.query.get(show)
        if 'series' in request.form and\
           len(request.form['series']) > 0 and\
           int(request.form['series']) > 0:
            show.series_id = int(request.form['series'])
        if 'tags' in request.form and\
           len(request.form['tags']) > 0:
            tags = Tag.parse_tags(request.form['tags'].replace(',',' '))
            show.add_tags(tags)
        if 'logo' in request.form and\
           len(request.form['logo']) > 0:
            show.logo = request.form['logo']
        rfk.database.session.commit()
        
    return jsonify({'success':True, 'data':None})

def _check_shows(begin, end):
    return Show.query.filter(Show.begin < end, Show.end > begin).all()

@api.route('/site/nowplaying')
def now_playing():
    try:
        track = Track.current_track()
        show = Show.get_active_show()
        ret = {}
        if show:
            user = show.get_active_user()
            if show.end:
                end = int(to_user_timezone(show.end).strftime("%s"))*1000
            else:
                end = None
            ret['show'] = {'name': show.name,
                           'begin': int(to_user_timezone(show.begin).strftime("%s"))*1000,
                           'now': int(to_user_timezone(now()).strftime("%s"))*1000,
                           'end': end,
                           'logo': show.get_logo(),
                           'type': Show.FLAGS.name(show.flags)
                           }
            if show.series:
                ret['series'] = {'name': show.series.name}
            link_users = []
            for ushow in show.users:
                link_users.append(_make_user_link(ushow.user))
            ret['users'] = {'links': natural_join(link_users)}
        if track:
            ret['track'] = {'title': None,
                            'artist': None,
                            }
        if show:
            filter_begin = show.end
        else:
            filter_begin = now()
        nextshow = Show.query.filter(Show.begin >= filter_begin).order_by(Show.begin.asc()).first();
        if nextshow:
            ret['nextshow'] = {'name': nextshow.name,
                               'begin': int(to_user_timezone(nextshow.begin).strftime("%s"))*1000,
                               'logo': show.get_logo()}
            if nextshow.series:
                ret['nextshow']['series'] = nextshow.series.name
        return jsonify({'success':True, 'data':ret})
    except Exception as e:
        return jsonify({'success':False, 'data':e})

def _make_user_link(user):
    return '<a href="%s" title="%s">%s</a>' % ('#',user.username,user.username);