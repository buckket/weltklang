from functools import wraps, partial

from rfk.api import api
from rfk import exc as rexc
from flask import jsonify, request, g

import rfk.database
from rfk.database.base import User, News, ApiKey
from rfk.database.show import Show, UserShow, Tag
from rfk.database.track import Track, Artist, Title
from rfk.database.streaming import Listener

import rfk.helper
from rfk.helper import now

from rfk.liquidsoap import LiquidInterface

from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, between


def wrapper(data, ecode=0, emessage=None):
    return {'pyrfk': {'version': '0.1', 'codename': 'Weltklang'}, 'status': {'code': ecode, 'message': emessage}, 'data': data}


def check_auth(f=None, required_permissions=None):
    if f is None:
        return partial(check_auth, required_permissions=required_permissions)
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        def raise_error(text):
            response = jsonify(wrapper(None, 403, text))
            response.status_code = 403
            return response
        
        if not request.args.has_key('key'):
            return raise_error('api key missing')
            
        key = request.args.get('key')
        
        try:
            apikey = ApiKey.check_key(key)
        except rexc.api.KeyInvalidException:
            return raise_error('api key invalid')
        except rexc.api.KeyDisabledException:
            return raise_error('api key disabled')
        except rexc.api.FastQueryException:
            return raise_error('throttling')
        except:
            return raise_error('unknown error')
            
        if required_permissions != None:
            for required_permission in required_permissions:
                if not apikey.flag & required_permission:
                    return raise_error('Flag %s (%i) required' % (ApiKey.FLAGS.name(required_permission), required_permission))
        
        g.apikey = apikey
        
        return f(*args, **kwargs)
    return decorated_function


@api.route('/web/dj')
@check_auth()
## DONE
def dj():
    """Return complete dj information
    
    Keyword arguments:
        dj_id -- database id of the requested dj
        dj_name -- nickname of the requested dj
    
    At least one argument is required
    """
    
    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)
    
    if dj_id:
        result = User.get_user(id=dj_id)
    elif dj_name:
        result = User.get_user(username=dj_name)
    else:
        return jsonify(wrapper(None, 400, 'missing required query parameter'))
    
    if result:
        data = {'dj': {'dj_id': result.user, 'dj_name': result.username }}
    else:
        data = {'dj': None}
    return jsonify(wrapper(data))


@api.route('/web/current_dj')
@check_auth()
## DONE (for now) ##
def current_dj():
    """Return dj information for the currently streaming dj(s)
    
    Keyword arguments:
        None
    """
    
    result = UserShow.query.filter(UserShow.status == UserShow.STATUS.STREAMING).first()
    if result:
        data = {'current_dj': {'dj_id': result.user.user, 'dj_name': result.user.username, 'dj_status': result.status}} 
    else:
        data = {'current_dj': None}
    return jsonify(wrapper(data))


@api.route('/web/kick_dj')
@check_auth(required_permissions=[ApiKey.FLAGS.KICK])
## DONE ##
def kick_dj():
    """Kick the dj, who's currently connected to the streaming server
    
    Keyword arguments:
        None
    """
    
    def try_kick():
        try:
            li = LiquidInterface()
            li.connect()
            li.kick_harbor()
            li.close()
            return True
        except:
            return False
            
    result = UserShow.query.filter(UserShow.status == UserShow.STATUS.STREAMING).first()
    if result:
        if try_kick():
            data = {'kick_dj': {'dj_id': result.user.user, 'dj_name': result.user.username, 'success': True}}
        else:
            data = {'kick_dj': {'dj_id': result.user.user, 'dj_name': result.user.username, 'success': False}}
    else:
        data = {'kick_dj': None}
    return jsonify(wrapper(data))


@api.route('/web/current_show')
@check_auth()
## DONE ##
def current_show():
    """Return the currently running show
    
    Keyword arguments:
        None    
    """
    
    clauses = []
    clauses.append((between(datetime.utcnow(), Show.begin, Show.end)) | (Show.end == None))
    result = Show.query.filter(*clauses).order_by(Show.begin.desc(), Show.end.asc()).all()
    
    data = {'current_show': {}}
    if result:
        for show in result:
            
            begin = show.begin.isoformat()
            if show.end:
                end = show.end.isoformat()
            else:
                end = None
            
            dj = []
            connected = False
            for usershow in show.users:
                dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status })
                if usershow.status == UserShow.STATUS.STREAMING:
                    connected = True
                
            if (show.flags & Show.FLAGS.UNPLANNED and len(result) == 2) or len(result) == 1:
                target = 'running_show'
            if (show.flags & Show.FLAGS.PLANNED and len(result) == 2):
                target = 'planned_show'
                
            data['current_show'][target] = {
                'show_id': show.show,
                'show_name': show.name,
                'show_description': show.description,
                'show_flags': show.flags,
                'show_connected': connected,
                'show_begin': begin,
                'show_end': end,
                'dj': dj
            }
    else:
        data = {'current_show': None}
    return jsonify(wrapper(data))


@api.route('/web/next_shows')
@check_auth
## DONE ##
def next_shows():
    """Return the next planned show(s)
    
    Keyword arguments:
        dj_id -- filter by dj
        dj_name -- filter by dj
        limit -- limit the output (default=5)
    """
    
    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)
    limit = request.args.get('limit', 5)
    
    clauses = []
    clauses.append(Show.begin > datetime.utcnow())
    
    if dj_id:
        clauses.append(UserShow.user == User.get_user(id=dj_id))
    if dj_name:
        clauses.append(UserShow.user == User.get_user(username=dj_name))
        
    result = Show.query.filter(*clauses).order_by(Show.begin.asc()).limit(limit).all()
    
    data = {'next_shows': {'shows': []}}
    if result:
        for show in result:
            
            begin = show.begin.isoformat()
            end = show.end.isoformat()
            
            dj = []
            for usershow in show.users:
                dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status })
                
            data['next_shows']['shows'].append({
                'show_id': show.show,
                'show_name': show.name,
                'show_description': show.description,
                'show_flags': show.flags,
                'show_begin': begin,
                'show_end': end,
                'dj': dj
            })
    else:
        data = {'next_shows': None}
    return jsonify(wrapper(data))


@api.route('/web/last_shows')
@check_auth
## DONE ##
def last_shows():
    """Return show history
    
    Keyword arguments:
        dj_id -- filter by dj
        dj_name -- filter by dj
        limit -- limit the output (default=5)
    """
    
    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)
    limit = request.args.get('limit', 5)
    
    clauses = []
    clauses.append(Show.end < datetime.utcnow())
    
    if dj_id:
        clauses.append(UserShow.user == User.get_user(id=dj_id))
    if dj_name:
        clauses.append(UserShow.user == User.get_user(username=dj_name))
        
    result = Show.query.filter(*clauses).order_by(Show.begin.desc()).limit(limit).all()
    
    data = {'last_shows': {'shows': []}}
    if result:
        for show in result:
            
            begin = show.begin.isoformat()
            end = show.end.isoformat()
            
            dj = []
            for usershow in show.users:
                dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status })
                
            data['last_shows']['shows'].append({
                'show_id': show.show,
                'show_name': show.name,
                'show_description': show.description,
                'show_flags': show.flags,
                'show_begin': begin,
                'show_end': end,
                'dj': dj
            })
    else:
        data = {'last_shows': None}
    return jsonify(wrapper(data))
   

@api.route('/web/current_track')
@check_auth
## DONE ##
def current_track():
    """Return the currently playing track
    
    Keyword arguments:
        None
    """

    result = Track.current_track()
    if result:
        data = {'current_track' : {
            'track_id': result.track,
            'track_begin': result.begin.isoformat(),
            'track_title': result.title.name,
            'track_artist': result.title.artist.name
        }}  
    else:
        data = {'current_track': None}
    return jsonify(wrapper(data))


@api.route('/web/last_tracks')
@check_auth
## DONE ##
def last_tracks():
    """Return the last played tracks
    
    Keyword arguments:
        dj_id -- filter by dj
        dj_name -- filter by dj
        limit -- limit the output (default=5)
    """
    
    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)
    limit = request.args.get('limit', 5)
    limit = limit if limit <= 50 else 50
    
    clauses = []
    clauses.append(Track.end < datetime.utcnow())
    
    if dj_id:
        clauses.append(UserShow.user == User.get_user(id=dj_id))
    if dj_name:
        clauses.append(UserShow.user == User.get_user(username=dj_name))
        
    result = Track.query.filter(*clauses).order_by(Track.end.desc()).limit(limit).all()
    
    data = {'last_tracks': {'tracks': []}}
    if result:
        for track in result:
            
            begin = track.begin.isoformat()
            end = track.end.isoformat()
            
            data['last_tracks']['tracks'].append({
                'track_id': track.track,
                'track_begin': begin,
                'track_end': end,
                'track_title': track.title.name,
                'track_artist': track.title.artist.name
            })
    else:
        data = {'last_tracks': None}
    return jsonify(wrapper(data))


@api.route('/web/listener')
@check_auth
## DONE ##
def listener():
    """Return current listener count
    
    Keyword arguments:
        None
    """
    
    clauses = []
    clauses.append(Listener.disconnect == None)
    
    result = Listener.query.filter(*clauses).all()
    
    data = {'listener': {'listener': []}}
    temp = {'per_stream': {}, 'per_country': {}, 'total_count': len(result)}
    
    if result:
        
        for listener in result:
            
            stream = listener.stream_relay.stream
            try: 
                temp['per_stream'][stream.code]['count'] += 1
            except KeyError:
                temp['per_stream'][stream.code] = {'count': 1, 'name': stream.name}
                
            country = listener.country
            try: 
                temp['per_country'][country]['count'] += 1
            except KeyError:
                temp['per_country'][country] = {'count': 1}
            
    data['listener'] = temp
    return jsonify(wrapper(data))
    