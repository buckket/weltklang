from functools import wraps, partial
from flask import Blueprint, g, request, jsonify

import rfk.database
from rfk.database.base import ApiKey
from rfk import exc as rexc

api = Blueprint('api', __name__)


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


from .web import *
from .site import *
from .locale_timezone import *


@api.route('/<path:path>')
def page_not_found(path):
    response = jsonify(wrapper(None, 404, "'%s' not found" % (path)))
    response.status_code = 404
    return response
