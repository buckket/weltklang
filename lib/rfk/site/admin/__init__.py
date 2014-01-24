from flask import Blueprint, render_template, url_for, request
from flask.ext.login import login_required, current_user

from rfk.database.base import User
from rfk.site.helper import permission_required, paginate, pagelinks


admin = Blueprint('admin', __name__)

import relays
import streams
import loops
import liquidsoap
import logs
import listener
import tags


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
    pagination = pagelinks('.user_list', page, total_pages)
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
        entries.append(['admin.user_list', 'Users', 'admin'])
        entries.append(['admin.log_list', 'Logs', 'admin'])
        entries.append(['admin.listener_list', 'Listeners', 'admin'])
    for entry in entries:
        active = endpoint == entry[0]
        menu['submenu'].append({'name': entry[1],
                                'url': url_for(entry[0]),
                                'active': (active)})
        if active:
            menu['active'] = True
    return menu


admin.create_menu = create_menu
