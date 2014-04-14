from flask import render_template, request
from flask.ext.login import login_required, current_user

from rfk.database.base import Log
from rfk.site.helper import permission_required, paginate_query, Pagination

from ..admin import admin


@admin.route('/logs/', defaults={'page': 1})
@admin.route('/logs/page/<int:page>')
@login_required
@permission_required(permission='admin')
def log_list(page):
    per_page = 25
    (logs, total_count) = paginate_query(Log.query.order_by(Log.timestamp.desc()), page=page)
    pagination = Pagination(page, per_page, total_count)
    return render_template('admin/logs_list.html', logs=logs, pagination=pagination)
