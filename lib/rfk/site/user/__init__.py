from flask import Blueprint, render_template, abort

from rfk.helper import now, iso_country_to_countryball
from rfk.database.base import User
from rfk.database.show import Show, UserShow

user = Blueprint('user', __name__)
import apikey


@user.route('/<user>')
def info(user):
    user = User.get_user(username=user)

    upcoming_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.begin >= now()).order_by(
        Show.begin.asc()).limit(5).all()
    last_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.end <= now()).order_by(
        Show.end.desc()).limit(5).all()
    if user:
        ball = iso_country_to_countryball(user.country)
        return render_template('user/info.html',
                               username=user.username,
                               ball=ball,
                               st=user.get_total_streamtime(),
                               shows={'upcoming': upcoming_shows, 'last': last_shows})
    else:
        abort(404)
