'''
Created on Aug 11, 2012

@author: teddydestodes
'''

from flask import Blueprint, render_template, g
from functools import wraps
import rfk
from flask.ext.login import login_required, current_user

admin = Blueprint('admin',__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_permission('admin'):
            return 'you need to be an admin'
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@admin.route('/streams')
@login_required
def streams():
    return render_template('admin/streams.html')

@admin.route('/liquidsoap')
@login_required
def liquidsoap():
    return render_template('admin/streams.html')