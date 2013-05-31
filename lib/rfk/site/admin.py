'''
Created on Aug 11, 2012

@author: teddydestodes
'''
from flask import Blueprint, render_template, url_for, request, redirect
from functools import wraps
import rfk
import rfk.liquidsoap
import rfk.site
from rfk.site.helper import permission_required
from rfk.site.forms.stream import new_stream
from rfk.site.forms.relay import new_relay
from flask.ext.login import login_required, current_user

import rfk.database
from rfk.database.streaming import Stream, Relay
from rfk.exc.streaming import CodeTakenException, InvalidCodeException, MountpointTakenException, MountpointTakenException,\
    AddressTakenException

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

@admin.route('/stream')
@login_required
@permission_required(permission='manage-liquidsoap')
def stream_list():
    streams = Stream.query.all()
    return render_template('admin/stream/list.html', streams=streams)

@admin.route('/stream/add', methods=['GET', 'POST'])
@login_required
@permission_required(permission='manage-liquidsoap')
def stream_add():
    form = new_stream(request.form)
    if request.method == 'POST' and form.validate():
        try:
            if form.type.data != 0:
                Stream.add_stream(form.code.data, form.name.data, form.mount.data, form.type.data, form.quality.data)
                rfk.database.session.commit()
                return redirect(url_for('.stream_list'))
            else:
                form.type.errors.append('Invalid type')
        except InvalidCodeException as e:
            form.code.errors.append('Invalid Chars')
        except CodeTakenException as e:
            form.code.errors.append('Identifier Taken')
        except MountpointTakenException as e:
            form.mount.errors.append('Mountpoint already taken')
    return render_template('admin/stream/streamform.html', form=form)

@admin.route('/relay')
@login_required
@permission_required(permission='manage-liquidsoap')
def relay_list():
    relays = Relay.query.all()
    return render_template('admin/relay/list.html', relays=relays)

@admin.route('/relay/add', methods=['GET', 'POST'])
@login_required
@permission_required(permission='manage-liquidsoap')
def relay_add():
    form = new_relay(request.form)
    if request.method == 'POST' and form.validate():
        try:
            relay = Relay.add_relay(form.address.data, form.port.data, form.bandwidth.data,
                                    form.admin_username.data, form.admin_password.data,
                                    form.auth_username.data,form.auth_password.data,
                                    form.relay_username.data, form.relay_password.data, form.type.data)
            rfk.database.session.commit()
        except AddressTakenException:
            form.address.errors.append('Address already in Database')
            form.port.errors.append('Address already in Database')
        pass
    return render_template('admin/relay/relayform.html', form=form)

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