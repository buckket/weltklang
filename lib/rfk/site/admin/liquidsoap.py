from flask import Blueprint, render_template, url_for, request, redirect
from functools import wraps
import math
import rfk
from rfk.helper import get_path
import rfk.liquidsoap
import rfk.site
from rfk.site.helper import permission_required
from rfk.site.forms.stream import new_stream
from rfk.site.forms.relay import new_relay
from flask.ext.login import login_required, current_user

import rfk.database
from rfk.database.base import User, Loop
from rfk.database.streaming import Stream, Relay
from rfk.exc.streaming import CodeTakenException, InvalidCodeException, MountpointTakenException, MountpointTakenException,\
    AddressTakenException
from flask.helpers import flash

from ..admin import admin

@admin.route('/liquidsoap/manage')
@login_required
@permission_required(permission='manage-liquidsoap')
def liquidsoap_manage():
    return render_template('admin/liquidsoap/management.html')

@admin.route('/liquidsoap/config')
@login_required
@permission_required(permission='manage-liquidsoap')
def liquidsoap_config():
    config = rfk.liquidsoap.gen_script().encode('utf-8')
    return render_template('admin/liquidsoap/config.html', liq_config=config)
