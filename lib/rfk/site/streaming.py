from flask import Blueprint, render_template, url_for, request, redirect
import rfk.database
from rfk import CONFIG
from rfk.helper import natural_join, make_user_link
from rfk.site import get_datetime_format
from rfk.site.forms.show import new_series_form
from flask.ext.login import login_required, current_user
from flask.ext.babel import to_user_timezone, to_utc
import datetime
import pytz


streaming = Blueprint('streaming',__name__)

@streaming.route('/nowplaying')
def now_playing():
    return ''
    