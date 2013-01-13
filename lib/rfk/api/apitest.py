import rfk
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
    id = request.args.get('id', None)
    name = request.args.get('name', None)
    
    if id:
        result = User.get_user(id=id)
    elif name:
        result = User.get_user(username=name)
    else:
        return jsonify(wrapper(None, 400, 'missing required query parameter'))
    
    if result:
        data = {'dj': {'id': result.user, 'name': result.username }}
    else:
        data = {'dj': None}
    return jsonify(wrapper(data))


@api.route('/web/current_dj')
@check_auth()
## BROKEN ##
def current_dj():
    result = db.session.query(rfk.User).filter(rfk.User.status == rfk.User.STATUS.STREAMING).first()
    if result:
        data = {'current_dj': {'id': result.user, 'name': result.name, 'status': result.status}} 
    else:
        data = {'current_dj': None}
    return jsonify(wrapper(data))


@api.route('/web/kick_dj')
@check_auth(required_permissions=[ApiKey.FLAGS.KICK])
## TODO ##
def kick_dj():
    return "TODO"


@api.route('/web/current_show')
@check_auth()
## DONE ##
def current_show():
    clauses = []
    clauses.append(and_(Show.begin <= datetime.utcnow(), or_(Show.end >= datetime.utcnow(), Show.end == None)))
    result = Show.query.join(UserShow).join(User).filter(*clauses).order_by(Show.begin.desc(), Show.end.asc()).all()
    
    data = {'current_show': {'shows': {}}}
    if result:
        for show in result:
            
            show.begin = show.begin.isoformat()
            if show.end:
                show.end = show.end.isoformat()
            
            dj = []
            for usershow in show.users:
                dj.append({'name': usershow.user.username, 'id': usershow.user.user, 'status': usershow.status })
                
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
