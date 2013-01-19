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
    id -- database id of the requested dj
    name -- nickname of the requested dj
    
    At least one argument is required
    """
    
    dj_id = request.args.get('id', None)
    dj_name = request.args.get('name', None)
    
    if dj_id:
        result = User.get_user(id=dj_id)
    elif dj_name:
        result = User.get_user(username=dj_name)
    else:
        return jsonify(wrapper(None, 400, 'missing required query parameter'))
    
    if result:
        data = {'dj': {'id': result.user, 'username': result.username }}
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
        data = {'current_dj': {'userid': result.user.user, 'username': result.user.username, 'status': result.status}} 
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
            data = {'kick_dj': {'userid': result.user.user, 'username': result.user.username, 'success': True}}
        else:
            data = {'kick_dj': {'userid': result.user.user, 'username': result.user.username, 'success': False}}
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
    
    data = {'current_show': {'shows': {}}}
    if result:
        for show in result:
            
            show.begin = show.begin.isoformat()
            if show.end:
                show.end = show.end.isoformat()
            
            dj = []
            for usershow in show.users:
                dj.append({'username': usershow.user.username, 'userid': usershow.user.user, 'status': usershow.status })
                
            if (show.flags & Show.FLAGS.UNPLANNED and len(result) == 2) or len(result) == 1:
                data['current_show']['show'] = show.show
            if (show.flags & Show.FLAGS.PLANNED and len(result) == 2):
                data['current_show']['planned'] = show.show
                
            data['current_show']['shows'][show.show] = {
                'name': show.name,
                'description': show.description,
                'flags': show.flags,
                'begin': show.begin,
                'end': show.end,
                'dj': dj
            }
    else:
        data = {'current_show': None}
    return jsonify(wrapper(data))
