import rfk
from rfk.api import api, check_auth, wrapper
from flask import jsonify, request, g

import datetime
from sqlalchemy import func, and_, or_, between


@api.route('/web/dj')
@check_auth()
def dj():
    id = request.args.get('id', None)
    name = request.args.get('name', None)
    
    if id:
        result = db.session.query(rfk.User).get(id)
    elif name:
        result = db.session.query(rfk.User).filter(rfk.User.name == name).first()
    else:
        return jsonify(wrapper(None, 400, 'missing required query parameter'))
    
    if result:
        data = {'dj': {'id': result.user, 'name': result.name, 'status': result.status}}
    else:
        data = {'dj': None}
    return jsonify(wrapper(data))


@api.route('/web/current_dj')
@check_auth()
def current_dj():
    result = db.session.query(rfk.User).filter(rfk.User.status == rfk.User.STATUS.STREAMING).first()
    if result:
        data = {'current_dj': {'id': result.user, 'name': result.name, 'status': result.status}} 
    else:
        data = {'current_dj': None}
    return jsonify(wrapper(data))


@api.route('/web/kick_dj')
@check_auth(required_permissions=[rfk.ApiKey.FLAGS.KICK])
def kick_dj():
    return "TODO"


@api.route('/web/current_show')
@check_auth()
def current_show():
    clauses = []
    clauses.append(and_(rfk.Show.begin <= datetime.datetime.now(), or_(rfk.Show.end >= datetime.datetime.now(), rfk.Show.end == None)))
    result = db.session.query(rfk.Show).join(rfk.UserShow).join(rfk.User).filter(*clauses).order_by(rfk.Show.begin.desc(), rfk.Show.end.asc()).all()
    
    data = {'current_show': {'shows': {}}}
    if result:
        for show in result:
            
            show.begin = show.begin.isoformat()
            if show.end:
                show.end = show.end.isoformat()
            
            dj = []
            for usershow in show.user_shows:
                dj.append({'name': usershow.user.name, 'id': usershow.user.user, 'status': usershow.user.status})
                
            if (show.flags & rfk.Show.FLAGS.UNPLANNED and len(result) == 2) or len(result) == 1:
                data['current_show']['show'] = show.show
            if (show.flags & rfk.Show.FLAGS.PLANNED and len(result) == 2):
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
