from flask import Blueprint, render_template, abort
from flask.ext.babel import gettext

import rfk.exc

from rfk.helper import now
from rfk.database.base import User
from rfk.database.show import Show, UserShow
from rfk.database.stats import UserStatistic

user = Blueprint('user', __name__)
import apikey


@user.route('/<user>')
def info(user):
    try:
        user = User.get_user(username=user)
    except rfk.exc.base.UserNotFoundException:
        abort(404)

    # checking user rank
    if user.has_permission('admin'):
        rank = gettext('Admin')
    else:
        rank = gettext('User')

    # count planned and unplanned shows
    planned_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.flags == Show.FLAGS.PLANNED).count()
    unplanned_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.flags == Show.FLAGS.UNPLANNED).count()
    total_shows = planned_shows + unplanned_shows

    # list upcoming and recent shows
    upcoming_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.begin >= now()).order_by(
        Show.begin.asc()).limit(5).all()
    last_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.end <= now()).order_by(
        Show.end.desc()).limit(5).all()

    stats = {}
    for us in UserStatistic.query.filter(UserStatistic.user == user).all():
        stats[us.code] = us.statistic.current_value().value

    return render_template('user/info.html', TITLE=user.username,
                           user=user,
                           rank=rank,
                           planned_shows=planned_shows,
                           unplanned_shows=unplanned_shows,
                           total_shows=total_shows,
                           st=user.get_total_streamtime(),
                           shows={'upcoming': upcoming_shows, 'last': last_shows},
                           stats=stats)
