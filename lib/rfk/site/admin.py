'''
Created on Aug 11, 2012

@author: teddydestodes
'''
from flask import Blueprint, render_template, url_for
from functools import wraps
import rfk
import rfk.liquidsoap
import rfk.site
from rfk.site.helper import permission_required
from flask.ext.login import login_required, current_user

admin = Blueprint('admin',__name__)

@admin.route('/')
@login_required
@permission_required(permission='admin')
def index():
    return render_template('admin/index.html')

@admin.route('/streams')
@login_required
def streams():
    return render_template('admin/streams.html')

@admin.route('/liquidsoap/manage')
@login_required
@permission_required(permission='manage-liquidsoap')
def liquidsoap_manage():
    return render_template('admin/liquidsoap/management.html')

@admin.route('/liquidsoap/config')
@login_required
@permission_required(permission='manage-liquidsoap')
def liquidsoap_config():
    config = rfk.liquidsoap.gen_script(rfk.site.app.config['BASEDIR']).encode('utf-8')
    return render_template('admin/liquidsoap/config.html', liq_config=config)

def create_menu(endpoint):
    if not current_user.has_permission(code='admin'):
        return False
    menu = {'name': 'Admin', 'submenu': [], 'active': False}
    entries = []
    if current_user.has_permission(code='manage-liquidsoap'):
        entries.append(['admin.liquidsoap_manage', 'Liquidsoapmanager', 'admin'])
        entries.append(['admin.liquidsoap_config', 'Liquidsoapconfig', 'admin'])
    for entry in entries:
        active = endpoint == entry[0]
        menu['submenu'].append({'name': entry[1],
                                'url': url_for(entry[0]),
                                'active': (active)})
        if active:
            menu['active'] = True
    return menu

admin.create_menu = create_menu