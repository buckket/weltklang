from rfk.api import api

@api.route('/apitest')
def apitest():
    return "LOLAPITEST"
    