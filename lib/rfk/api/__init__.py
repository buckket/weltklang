from flask import Blueprint
from flask import request, jsonify


api = Blueprint('api', __name__)
def wrapper(data, ecode=0, emessage=None):
    return {'pyrfk':{'version':'0.1','codename':'Affenkot'},'error':{'code':ecode,'message':emessage},'data':data}
    
from .apitest import *
#from .webapi import *
#from .icecast import *


@api.before_request
def check_auth():
    if not request.args.has_key('key'):
        response = jsonify(wrapper(None, 403, 'no api auth key given'))
        response.status_code = 403
        return response


@api.route('/')
def index():
    return "LOLAPI"

@api.route('/<path:path>')
def page_not_found(path):
    response = jsonify(wrapper(None, 404, "'%s' not found" % (path,)))
    response.status_code = 404
    return response



    

