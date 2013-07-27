from flask import Blueprint, render_template, url_for, request, redirect
from functools import wraps
import math
import rfk
from rfk.helper import get_path
import rfk.liquidsoap
import rfk.site
from rfk.site.helper import permission_required, paginate, pagelinks
from rfk.site.forms.stream import new_stream
from rfk.site.forms.relay import new_relay
from flask.ext.login import login_required, current_user

import rfk.database
from rfk.database.base import User, Loop
from rfk.database.streaming import Stream, Relay
from rfk.exc.streaming import CodeTakenException, InvalidCodeException, MountpointTakenException, MountpointTakenException,\
    AddressTakenException
from flask.helpers import flash

admin = Blueprint('admin',__name__)

import relays
import streams
import loops
import liquidsoap
import logs

@admin.route('/')
@login_required
@permission_required(permission='admin')
def index():
    return render_template('admin/index.html')

@admin.route('/user', methods=['GET'])
@login_required
@permission_required(permission='manage-liquidsoap')
def user_list():
    page = int(request.args.get('page') or 0)
    (users, total_pages) = paginate(User.query, page=page)
    pagination = pagelinks('.user_list',page ,total_pages)
    return render_template('admin/user/list.html', users=users, pagination=pagination)
        
def create_menu(endpoint):
    if not current_user.has_permission(code='admin'):
        return False
    menu = {'name': 'Admin', 'submenu': [], 'active': False}
    entries = []
    if current_user.has_permission(code='manage-liquidsoap'):
        entries.append(['admin.liquidsoap_manage', 'Liquidsoap-Manager', 'admin'])
        entries.append(['admin.liquidsoap_config', 'Liquidsoap-Config', 'admin'])
        entries.append(['admin.stream_list', 'Streams', 'admin'])
        entries.append(['admin.relay_list', 'Relays', 'admin'])
    for entry in entries:
        active = endpoint == entry[0]
        menu['submenu'].append({'name': entry[1],
                                'url': url_for(entry[0]),
                                'active': (active)})
        if active:
            menu['active'] = True
    return menu

admin.create_menu = create_menu