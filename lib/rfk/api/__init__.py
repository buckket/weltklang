import rfk
from rfk.site import db
from functools import wraps
from flask import Blueprint
from flask import g, request, jsonify

api = Blueprint('api', __name__)

def wrapper(data, ecode=0, emessage=None):
    return {'pyrfk':{'version':'0.1','codename':'Affenkot'},'status':{'code':ecode,'message':emessage},'data':data}

def check_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.args.has_key('key'):
            response = jsonify(wrapper(None, 403, 'api key missing'))
            response.status_code = 403
            return response
        g.key = "PENIS"
        return f(*args, **kwargs)
    return decorated_function

 
from .apitest import *
#from .webapi import *
from .icecast import *


@api.route('/<path:path>')
def page_not_found(path):
    response = jsonify(wrapper(None, 404, "'%s' not found" % (path,)))
    response.status_code = 404
    return response

    

