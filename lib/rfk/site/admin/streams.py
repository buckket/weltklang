from flask import render_template, url_for, request, redirect
from flask.ext.login import login_required, current_user

import rfk
import rfk.site
import rfk.database
import rfk.liquidsoap
from rfk.site.helper import permission_required
from rfk.site.forms.stream import new_stream
from rfk.database.streaming import Stream, Relay
from rfk.exc.streaming import CodeTakenException, InvalidCodeException, MountpointTakenException

from ..admin import admin


@admin.route('/streams')
@login_required
def streams():
    return render_template('admin/streams.html')


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
