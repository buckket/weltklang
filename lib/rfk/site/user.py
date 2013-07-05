from flask import Blueprint, Flask, session, g, render_template, flash, redirect, url_for, request, jsonify, abort


import rfk
from rfk.helper import now
import rfk.database
from rfk.database.base import User, ApiKey
from rfk.database.show import Show, UserShow
from flask.ext.login import login_required, current_user
from rfk.site.forms.apikey import new_apikey_form

from datetime import datetime, timedelta

user = Blueprint('user',__name__)


@user.route('/<user>/apikeys', methods=['GET', 'POST'])
@login_required
def apikey_list(user):
    from rfk.site import app
    apikeys = ApiKey.query.filter(ApiKey.user == current_user).all()
    form = new_apikey_form(request.form)
    if request.method == 'POST' and form.validate():
        apikey = ApiKey(application=form.application.data,
                        description=form.description.data,
                        user=current_user)
        apikey.gen_key()
        rfk.database.session.add(apikey)
        rfk.database.session.commit()
        form.application.data = ''
        form.description.data = ''
    return render_template('user/apikeys.html',apikeys=apikeys, form=form)

@user.route('/<user>')
def info(user):
    user = User.get_user(username=user)
    
    upcoming_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.begin >= now()).order_by(Show.begin.asc()).limit(5).all()
    last_shows = Show.query.join(UserShow).filter(UserShow.user == user, Show.end <= now()).order_by(Show.end.desc()).limit(5).all()
    if user:
        return render_template('user/info.html',
                               username=user.username,
                               st=user.get_total_streamtime(),
                               shows={'upcoming': upcoming_shows , 'last': last_shows})
    else:
        abort(404)
