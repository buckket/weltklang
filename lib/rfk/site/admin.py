'''
Created on Aug 11, 2012

@author: teddydestodes
'''
from flask import Blueprint, render_template, url_for
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
    return render_template('admin/liquidsoap.html')


def create_menu(endpoint):
    menu = {'name': 'Admin', 'submenu': [], 'active': False}
    entries = [['admin.liquidsoap', 'Liquidsoap', 'admin'],
               ]
    for entry in entries:
        active = endpoint == entry[0]
        menu['submenu'].append({'name': entry[1],
                                'url': url_for(entry[0]),
                                'active': (active)})
        if active:
            menu['active'] = True
    return menu

admin.create_menu = create_menu