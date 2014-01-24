from flask import render_template, request
from flask.ext.login import login_required, current_user

import rfk
import rfk.site
import rfk.database
import rfk.liquidsoap
from rfk.site.helper import permission_required
from rfk.site.forms.relay import new_relay
from rfk.database.streaming import Relay
from rfk.exc.streaming import AddressTakenException

from ..admin import admin


@admin.route('/relay')
@login_required
@permission_required(permission='manage-liquidsoap')
def relay_list():
    relays = Relay.query.all()
    return render_template('admin/relay/list.html', relays=relays)


@admin.route('/relay/<int:relay>')
@login_required
@permission_required(permission='manage-liquidsoap')
def relay(relay):
    relay = Relay.query.get(relay)
    return render_template('admin/relay/show.html', relay=relay)


@admin.route('/relay/add', methods=['GET', 'POST'])
@login_required
@permission_required(permission='manage-liquidsoap')
def relay_add():
    form = new_relay(request.form)
    if request.method == 'POST' and form.validate():
        try:
            relay = Relay.add_relay(form.address.data, form.port.data, form.bandwidth.data,
                                    form.admin_username.data, form.admin_password.data,
                                    form.auth_username.data, form.auth_password.data,
                                    form.relay_username.data, form.relay_password.data, form.type.data)
            rfk.database.session.commit()
        except AddressTakenException:
            form.address.errors.append('Address already in Database')
            form.port.errors.append('Address already in Database')
    return render_template('admin/relay/relayform.html', form=form)
