from rfk.api import api, check_auth, wrapper
from flask import jsonify, request, g

import rfk.database
from rfk.database.base import User, News, ApiKey
from rfk.database.show import Show, UserShow, Tag

from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, between


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
    
    result = UserShow.query.join(User).filter(UserShow.status == UserShow.STATUS.STREAMING).first()
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
    
    # just a testing dummy
    def do_kick_dj(dj):
        return True
    
    result = UserShow.query.join(User).filter(UserShow.status == UserShow.STATUS.STREAMING).first()
    if result:
        if do_kick_dj(result.user.user):
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
    result = Show.query.join(UserShow).join(User).filter(*clauses).order_by(Show.begin.desc(), Show.end.asc()).all()
    
    data = {'current_show': {}}
    if result:
        for show in result:
            
            show.begin = show.begin.isoformat()
            if show.end:
                show.end = show.end.isoformat()
            
            dj = []
            for usershow in show.users:
                dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status })
                
            if (show.flags & Show.FLAGS.UNPLANNED and len(result) == 2) or len(result) == 1:
                target = 'running_show'
            if (show.flags & Show.FLAGS.PLANNED and len(result) == 2):
                target = 'planned_show'
                
            data['current_show'][target] = {
                'show_id': show.show,
                'show_name': show.name,
                'show_description': show.description,
                'show_flags': show.flags,
                'show_begin': show.begin,
                'show_end': show.end,
                'dj': dj
            }
    else:
        data = {'current_show': None}
    return jsonify(wrapper(data))


@api.route('/web/next_shows')
@check_auth
## WIP ##
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
        
    result = Show.query.join(UserShow).join(User).filter(*clauses).order_by(Show.begin.asc()).limit(limit).all()
    
    data = {'next_shows': {'shows': []}}
    if result:
        for show in result:
            
            show.begin = show.begin.isoformat()
            show.end = show.end.isoformat()
            
            dj = []
            for usershow in show.users:
                dj.append({'dj_name': usershow.user.username, 'dj_id': usershow.user.user, 'status': usershow.status })
                
            data['next_shows']['shows'].append({
                'show_id': show.show,
                'show_name': show.name,
                'show_description': show.description,
                'show_flags': show.flags,
                'show_begin': show.begin,
                'show_end': show.end,
                'dj': dj
            })
    else:
        data = {'next_shows': None}
    return jsonify(wrapper(data))
    
    