from flask import Blueprint, render_template, url_for, request, redirect
from functools import wraps
import math
import rfk
from rfk.helper import get_path
import rfk.liquidsoap
import rfk.site
from rfk.site.helper import permission_required, pagelinks, paginate
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

@admin.route('/liquidsoap/loops', methods=['GET','POST'])
@login_required
@permission_required(permission='manage-liquidsoap')
def loop_list():
    if request.method == 'POST':
        if request.form.get('action') == 'add':
 #           try:
            spl = request.form.get('begin').split(':')
            begin = int(int(spl[0])*100+(int(spl[1])/60.)*100)
            spl = request.form.get('end').split(':')
            end = math.ceil(int(spl[0])*100+(int(spl[1])/60.)*100)
            if end == begin and end == 0:
                end = 2400
            loop = Loop(begin=begin, end=end, filename=request.form.get('filename'))
            rfk.database.session.add(loop)
            rfk.database.session.commit()
#            except Exception as e:
#                flash('error while inserting Loop')
        elif request.form.get('action') == 'delete':
            try:
                rfk.database.session.delete(Loop.query.get(request.form.get('loopid')))
                rfk.database.session.commit()
            except Exception as e:
                flash('error while deleting Loop')
    page = int(request.args.get('page') or 0)
    (result, total_pages) = paginate(Loop.query, page=page)
    current_loop = Loop.get_current_loop()
    loops = []
    for loop in result:
        loops.append({'loop': loop.loop,
                      'begin': '%02d:%02d' % (int(loop.begin/100), int(((loop.begin%100)/100.)*60)),
                      'end': '%02d:%02d' % (int(loop.end/100), int(((loop.end%100)/100.)*60)),
                      'current': loop == current_loop,
                      'filename': loop.filename,
                      'file_missing': not(loop.file_exists)})
    pagination = pagelinks('.loop_list',page ,total_pages)
    searchpath = get_path(rfk.CONFIG.get('liquidsoap', 'looppath'))
    return render_template('admin/loops/list.html', loops=loops, pagination=pagination, searchpath=searchpath)
