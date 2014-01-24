from flask import render_template, request
from flask.ext.login import login_required, current_user

from rfk.database.base import Log
from rfk.site.helper import permission_required, paginate, pagelinks

from ..admin import admin


@admin.route('/logs', methods=['GET'])
@login_required
@permission_required(permission='admin')
def log_list():
    page = int(request.args.get('page') or 0)
    (logs, total_pages) = paginate(Log.query.order_by(Log.timestamp.desc()), page=page)
    pagination = pagelinks('.log_list', page, total_pages)
    return render_template('admin/logs.html', logs=logs, pagination=pagination)
