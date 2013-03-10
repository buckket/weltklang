'''
Created on Mar 10, 2013

@author: teddydestodes
'''

from flask import jsonify, request, g, render_template
import pytz

from rfk.api import api, check_auth, wrapper
from rfk.site import app, locales

@api.route("/site/timezoneselector")
def timezoneselector():
    return render_template('timezoneselector.html', timezones=pytz.common_timezones, locales=locales)

@api.route("/site/localeinfo/<string:locale>")
def localeinfo(locale):
    return jsonify(locales[locale])