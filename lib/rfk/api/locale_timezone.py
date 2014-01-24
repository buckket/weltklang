import pytz

from flask import jsonify, render_template

from rfk.api import api
from rfk.site import locales


@api.route("/site/timezoneselector")
def timezoneselector():
    return render_template('timezoneselector.html', timezones=pytz.common_timezones, locales=locales)


@api.route("/site/localeinfo/<string:locale>")
def localeinfo(locale):
    return jsonify(locales[locale])
