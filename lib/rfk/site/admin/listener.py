from flask import render_template
from flask.ext.login import login_required, current_user

from rfk.site.helper import permission_required
from rfk.database.streaming import Listener

from ..admin import admin


@admin.route('/listener')
@login_required
@permission_required(permission='admin')
def listener_list():
    listener = Listener.get_current_listeners()
    return render_template('admin/listener_list.html', listeners=listener)
