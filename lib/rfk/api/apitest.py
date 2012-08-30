import rfk
from rfk.site import db
from rfk.api import api, check_auth, wrapper
from flask import jsonify, request, g


# DEBUG
@api.route('/web/gen_key')
def gen_key():
    key = rfk.ApiKey('Test', 'Test', rfk.User.get_user(db.session, username='MrLoom'))
    key.gen_key(db.session)
    db.session.commit()
    return key.key
# DEBUG

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
        data = {'dj': {'id': result.user, 'name': result.name, 'status': result.status}, 'key': g.key}
    else:
        data = {'dj': None}
    return jsonify(wrapper(data))
    
@api.route('/web/current_dj')
@check_auth()
def current_dj():
    result = db.session.query(rfk.User).filter(rfk.User.status == rfk.User.STATUS_STREAMING).first()
    if result:
        data = {'current_dj': {'id': result.user, 'name': result.name, 'status': result.status}} 
    else:
        data = {'current_dj': None}
    return jsonify(wrapper(data))

@api.route('/web/kick_dj')
@check_auth(required_permissions=[rfk.ApiKey.FLAG_KICK])
def kick_dj():
    return "TODO"
    