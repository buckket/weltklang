from flask import Blueprint

api = Blueprint('api', __name__)
from rfk.api.apitest import *
#from rfk.api.webapi import *
#from rfk.api.icecast import *
    
@api.route('/')
def index():
    return "LOLAPI"