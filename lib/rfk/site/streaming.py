from flask import Blueprint
from flask.ext.login import login_required, current_user
from flask.ext.babel import to_user_timezone, to_utc


streaming = Blueprint('streaming', __name__)

# What's that supposed do to?
@streaming.route('/nowplaying')
def now_playing():
    return ''
