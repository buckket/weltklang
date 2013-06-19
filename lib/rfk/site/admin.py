'''
Created on Aug 11, 2012

@author: teddydestodes
'''
from flask import Blueprint, render_template, url_for, request, redirect
from functools import wraps
import math
import rfk
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
                                    form.auth_username.data,form.auth_password.data,
                                    form.relay_username.data, form.relay_password.data, form.type.data)
            rfk.database.session.commit()
        except AddressTakenException:
            form.address.errors.append('Address already in Database')
            form.port.errors.append('Address already in Database')
    return render_template('admin/relay/relayform.html', form=form)

@admin.route('/user', methods=['GET'])
@login_required
@permission_required(permission='manage-liquidsoap')
def user_list():
    page = int(request.args.get('page') or 0)
    (users, total_pages) = _paginate(User, page=page)
    pagination = _pagelinks('.user_list',page ,total_pages)
    return render_template('admin/user/list.html', users=users, pagination=pagination)

@admin.route('/liquidsoap/loops', methods=['GET','POST'])
@login_required
@permission_required(permission='manage-liquidsoap')
def loop_list():
    if request.method == 'POST':
        if request.form.get('action') == 'add':
            try:
                spl = request.form.get('begin').split(':')
                begin = int(int(spl[0])*100+(int(spl[1])/60.)*100)
                spl = request.form.get('end').split(':')
                end = int(int(spl[0])*100+(int(spl[1])/60.)*100)
                loop = Loop(begin=begin, end=end, filename=request.form.get('filename'))
                rfk.database.session.add(loop)
                rfk.database.session.commit()
            except Exception as e:
                flash('error while inserting Loop')
        elif request.form.get('action') == 'delete':
            try:
                rfk.database.session.delete(Loop.query.get(request.form.get('loopid')))
                rfk.database.session.commit()
            except Exception as e:
                flash('error while inserting Loop')
    page = int(request.args.get('page') or 0)
    (result, total_pages) = _paginate(Loop, page=page)
    current_loop = Loop.get_current_loop()
    loops = []
    for loop in result:
        loops.append({'loop': loop.loop,
                      'begin': '%02d:%02d' % (int(loop.begin/100), int(((loop.begin%100)/100.)*60)),
                      'end': '%02d:%02d' % (int(loop.end/100), int(((loop.end%100)/100.)*60)),
                      'current': loop == current_loop,
                      'filename': loop.filename,
                      'file_missing': not(loop.file_exists)})
    pagination = _pagelinks('.loop_list',page ,total_pages)
    return render_template('admin/loops/list.html', loops=loops, pagination=pagination)


def _paginate(queryclass,page=0,per_page=25):
    result = queryclass.query.limit(per_page).offset(page*per_page).all()
    total_pages = int(math.ceil(queryclass.query.count()/per_page))
    return (result, total_pages)

def _pagelinks(url, page, total_pages, visible_pages=7, param='page'):
    pagelinks = {'first': None,
                 'last': None,
                 'pages': []}
    if page > 0:
        pagelinks['first'] = url_for(url, **{param:0})
    if page < total_pages:
        pagelinks['last'] = url_for(url, **{param:total_pages})
    begin = int(page-(visible_pages/2))
    
    if begin+visible_pages > total_pages+1:
        begin = total_pages+1-visible_pages
    if begin < 0:
        begin = 0
    end = min(begin+visible_pages,total_pages+1)
    for pn in range(begin,end):
        pagelinks['pages'].append({'name':pn+1,
                                   'active': pn == page,
                                   'url': url_for(url, **{param:pn})})
    return pagelinks
        
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