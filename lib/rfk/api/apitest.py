from rfk.api import api, wrapper
from flask import jsonify

@api.route('/apitest')
def apitest():
    data = 'HUNDESOHN'
    return jsonify(wrapper(data))
    