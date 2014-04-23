__author__ = 'teddydestodes'
from flask import render_template
from flask.ext.login import login_required, current_user

from rfk.site.helper import permission_required

from ..admin import admin


@admin.route('/liquidsoap/config')
@login_required
@permission_required(permission='manage-donations')
def donations_list():
    return render_template('admin/donations/list.html', donations=donations)