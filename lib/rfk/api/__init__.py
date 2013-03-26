from flask import Blueprint, g, request, jsonify

import rfk.database
from rfk.database.base import ApiKey

api = Blueprint('api', __name__)


from .web import *
from .site import *
from .locale_timezone import *


@api.route('/<path:path>')
def page_not_found(path):
    response = jsonify(wrapper(None, 404, "'%s' not found" % (path)))
    response.status_code = 404
    return response
