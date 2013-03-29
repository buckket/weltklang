from flask import Blueprint, Flask, session, g, render_template, flash, redirect, url_for, request, jsonify


import rfk
from rfk.database import session
from rfk.database.base import User
from flask.ext.login import login_required, current_user

from datetime import datetime

user = Blueprint('user',__name__)


@user.route('/<user>')
def info(user):
    user = User.get_user(username=user)
    
    if user:
        return render_template('user/info.html', username=user.username, shows={'upcoming': [], 'last':[]})
    else:
        return render_template('user/info.html', undefined=True)
