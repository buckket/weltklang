import rfk
from rfk.site import db
from rfk.api import api, check_auth, wrapper
from flask import jsonify, request, g

import datetime
from sqlalchemy import func, and_, or_, between


@api.route('/web/dj')
#@check_auth()
def dj():
    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)
    
    if dj_id:
        result = db.session.query(rfk.User).get(dj_id)
    elif dj_name:
        result = db.session.query(rfk.User).filter(rfk.User.name == dj_name).first()
    else:
        return jsonify(wrapper(None, 400, 'missing required query parameter'))
    
    if result:
        data = {'dj': {'id': result.user, 'name': result.name, 'status': result.status}}
    else:
        data = {'dj': None}
    return jsonify(wrapper(data))


@api.route('/web/current_dj')
#@check_auth()
def current_dj():
    result = db.session.query(rfk.User).filter(rfk.User.status == rfk.User.STATUS.STREAMING).first()
    if result:
        data = {'current_dj': {'id': result.user, 'name': result.name, 'status': result.status}} 
    else:
        data = {'current_dj': None}
    return jsonify(wrapper(data))


@api.route('/web/kick_dj')
#@check_auth(required_permissions=[rfk.ApiKey.FLAGS.KICK])
def kick_dj():
    return "TODO"


@api.route('/web/current_show')
#@check_auth()
def current_show():
    clauses = []
    clauses.append(and_(rfk.Show.begin <= datetime.datetime.utcnow(), or_(rfk.Show.end >= datetime.datetime.utcnow(), rfk.Show.end == None)))
    result = db.session.query(rfk.Show).join(rfk.UserShow).join(rfk.User).filter(*clauses).order_by(rfk.Show.begin.desc(), rfk.Show.end.asc()).all()
    
    data = {'current_show': {}}
    if result:
        
        if len(result) >= 2:
            data['current_show']['overlap'] = True
        else:
            data['current_show']['overlap'] = False
            
        for show in result:
            
            show.begin = show.begin.isoformat()
            if show.end:
                show.end = show.end.isoformat()
            
            dj = []
            for usershow in show.user_shows:
                dj.append({'name': usershow.user.name, 'id': usershow.user.user, 'status': usershow.user.status})
                                
            if (show.flags & rfk.Show.FLAGS.UNPLANNED and len(result) == 2) or len(result) == 1:
                data['current_show']['show'] = {
                    'id': show.show,
                    'name': show.name,
                    'description': show.description,
                    'flags': show.flags,
                    'begin': show.begin,
                    'end': show.end,
                    'dj': dj
                }
            if (show.flags & rfk.Show.FLAGS.PLANNED and len(result) == 2):
                data['current_show']['planned_show'] = {
                    'id': show.show,
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


@api.route('/web/next_show')
#@check_auth()
def next_show():
    limit = request.args.get('limit', 1)
    dj_id = request.args.get('dj_id', None)
    dj_name = request.args.get('dj_name', None)

    clauses = []
    clauses.append(rfk.Show.begin > datetime.datetime.utcnow())
    if dj_id:
        clauses.append(rfk.User.user == dj_id)
    elif dj_name:
        clauses.append(rfk.User.name == dj_name)
    result = db.session.query(rfk.Show).join(rfk.UserShow).join(rfk.User).filter(*clauses).order_by(rfk.Show.begin.asc()).limit(limit).distinct().all()
    
    data = {'next_show': {'shows': []}}
    if result:
        for show in result:
            
            show.begin = show.begin.isoformat()
            if show.end:
                show.end = show.end.isoformat()
            
            dj = []
            for usershow in show.user_shows:
                dj.append({'name': usershow.user.name, 'id': usershow.user.user, 'status': usershow.user.status})
                
            data['next_show']['shows'].append({
                'id:': show.show,
                'name': show.name,
                'description': show.description,
                'flags': show.flags,
                'begin': show.begin,
                'end': show.end,
                'dj': dj
            })
    else:
        data = {'next_show': None}
    return jsonify(wrapper(data))
    
    
    
