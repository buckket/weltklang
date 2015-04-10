"""
    rfk.api.web
    ~~~~~~~~~~~

    A REST interface for PyRfK

"""

from functools import wraps, partial
from datetime import datetime

from sqlalchemy import between

from flask import jsonify, request, g

from rfk.api import api
from rfk import exc as rexc

import rfk.database
from rfk.database.base import User, ApiKey
from rfk.database.show import Show, UserShow
from rfk.database.track import Track
from rfk.database.streaming import Listener, Relay, Stream
from rfk.database.stats import Statistic, StatsistcsData

from rfk.liquidsoap import LiquidInterface
from rfk.exc.base import UserNotFoundException


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

        if not 'key' in request.args:
            return raise_error('api key missing')

        key = request.args.get('key')

        try:
            apikey = ApiKey.check_key(key)
            rfk.database.session.commit()
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
                    return raise_error(
                        'Flag %s (%i) required' % (ApiKey.FLAGS.name(required_permission), required_permission))

        g.apikey = apikey

        return f(*args, **kwargs)

    return decorated_function


@api.route('/web/<path:path>')
def page_not_found(path):
    response = jsonify(wrapper(None, 404, "'%s' not found" % path))
    response.status_code = 404
    return response


@api.route('/web/dj')
@check_auth()
## DONE
def dj():
    """Returns complete dj information

    Keyword arguments:
        - dj_id -- database id of the requested dj
        - dj_name -- nickname of the requested dj

    Returns:
        {'dj': {'dj_id': x, 'dj_name': x }}

    At least one argument is required
    """

    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)

    try:
        user = User.get_user(id=dj_id, username=dj_name)
        return jsonify(wrapper({'dj': {'dj_id': user.user, 'dj_name': user.username}}))
    except rexc.base.UserNotFoundException:
        return jsonify(wrapper({'dj': None}))
    except AssertionError:
        return jsonify(wrapper(None, 400, 'missing required query parameter'))


@api.route('/web/current_dj')
@check_auth()
## DONE (for now) ##
def current_dj():
    """Returns dj information for the currently streaming dj(s)

    Keyword arguments:
        - None

    Returns:
        {'current_dj': {'dj_id': x, 'dj_name': x, 'dj_status': x }}
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
    """Kicks the dj, who's currently connected to the streaming server

    Keyword arguments:
        - None

    Returns:
        {'kick_dj': {'dj_id': x, 'dj_name': x, 'success': x}}
    """

    def try_kick():
        try:
            li = LiquidInterface()
            li.connect()
            kicked = li.kick_harbor()
            li.close()
            return kicked
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
        - None
    """

    clauses = [(between(datetime.utcnow(), Show.begin, Show.end)) | (Show.end == None)]
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
                dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status})
                if usershow.status == UserShow.STATUS.STREAMING:
                    connected = True

            if (show.flags & Show.FLAGS.UNPLANNED and len(result) == 2) or len(result) == 1:
                target = 'running_show'
            if show.flags & Show.FLAGS.PLANNED and len(result) == 2:
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
        - dj_id -- filter by dj
        - dj_name -- filter by dj
        - limit -- limit the output (default=5)
    """

    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)
    limit = request.args.get('limit', 5)

    clauses = [Show.begin > datetime.utcnow()]

    try:
        if dj_id:
            clauses.append(UserShow.user == User.get_user(id=dj_id))
        if dj_name:
            clauses.append(UserShow.user == User.get_user(username=dj_name))

        result = Show.query.join(UserShow).filter(*clauses).order_by(Show.begin.asc()).limit(limit).all()

        data = {'next_shows': {'shows': []}}
        if result:
            for show in result:

                begin = show.begin.isoformat()
                end = show.end.isoformat()

                dj = []
                for usershow in show.users:
                    dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status})

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
    except UserNotFoundException:
        return jsonify(wrapper({'next_shows': None}))


@api.route('/web/last_shows')
@check_auth
## DONE ##
def last_shows():
    """Return show history

    Keyword arguments:
        - dj_id -- filter by dj
        - dj_name -- filter by dj
        - limit -- limit the output (default=5)
    """

    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)
    limit = request.args.get('limit', 5)

    clauses = [Show.end < datetime.utcnow()]

    try:
        if dj_id:
            clauses.append(UserShow.user == User.get_user(id=dj_id))
        if dj_name:
            clauses.append(UserShow.user == User.get_user(username=dj_name))

        result = Show.query.join(UserShow).filter(*clauses).order_by(Show.begin.desc()).limit(limit).all()

        data = {'last_shows': {'shows': []}}
        if result:
            for show in result:

                begin = show.begin.isoformat()
                end = show.end.isoformat()

                dj = []
                for usershow in show.users:
                    dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status})

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
    except UserNotFoundException:
        return jsonify(wrapper({'last_shows': None}))


@api.route('/web/current_track')
@check_auth
## DONE ##
def current_track():
    """Return the currently playing track

    Keyword arguments:
        - None
    """

    result = Track.current_track()
    if result:
        data = {'current_track': {
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
        - dj_id -- filter by dj
        - dj_name -- filter by dj
        - limit -- limit the output (default=5)
    """

    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)
    limit = int(request.args.get('limit', 5))
    limit = limit if limit <= 50 else 50

    clauses = [Track.end < datetime.utcnow()]

    if dj_id is not None:
        clauses.append(UserShow.user == User.get_user(id=dj_id))
    if dj_name is not None:
        clauses.append(UserShow.user == User.get_user(username=dj_name))

    result = Track.query.join(Show).join(UserShow).filter(*clauses).order_by(Track.end.desc()).limit(limit).all()

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
        - None
    """

    clauses = [Listener.disconnect == None]
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


@api.route('/web/active_relays')
@check_auth
## DONE ##
def active_relays():
    """Return information about all active relays

    Keyword arguments:
        - None
    """

    result = Relay.query.filter(Relay.status == Relay.STATUS.ONLINE).all()

    data = {'active_relays': {'relays': [], 'total_bandwidth': 0}}

    if result:
        for relay in result:
            data['active_relays']['relays'].append({
                'relay_id': relay.relay,
                'relay_type': relay.type,
                'relay_address': relay.address,
                'relay_max_bandwidth': relay.bandwidth,
                'relay_current_bandwidth': relay.usage
            })
            data['active_relays']['total_bandwidth'] += relay.usage
    else:
        data = {'active_relays': None}
    return jsonify(wrapper(data))


@api.route('/web/active_streams')
@check_auth
## DONE ##
def active_streams():
    """Return all available streams

    Keyword arguments:
        - None
    """

    result = Stream.query.all()

    data = {'active_streams': []}

    if result:
        for stream in result:
            data['active_streams'].append({
                'stream_id': stream.stream,
                'stream_mount': stream.mount,
                'stream_code': stream.code,
                'stream_name': stream.name,
                'stream_type': stream.type,
                'stream_quality': stream.quality
            })
    else:
        data = {'active_streams': None}
    return jsonify(wrapper(data))


@api.route('/web/listener_peak')
@check_auth
## DONE ##
def listener_peak():
    """Return the global listener peak

    Keyword arguments:
        - None
    """

    peak = StatsistcsData.query.join(Statistic).filter(Statistic.identifier == 'lst-total').order_by(StatsistcsData.value.desc()).first()
    if peak:
        data = {'listener_peak': {'peak_value': peak.value, 'peak_time': peak.timestamp.isoformat()}}

        show = Show.query.join(UserShow).filter(between(peak.timestamp, Show.begin, Show.end)).first()
        if show:
            dj = []
            for usershow in show.users:
                dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status})

            data['listener_peak']['peak_show'] = {
                'show_id': show.show,
                'show_name': show.name,
                'show_description': show.description,
                'show_flags': show.flags,
                'show_begin': show.begin.isoformat(),
                'show_end': show.end.isoformat(),
                'dj': dj
            }
        else:
            data['listener_peak']['peak_show'] = None
    else:
        data = {'listener_peak': None}
    return jsonify(wrapper(data))
