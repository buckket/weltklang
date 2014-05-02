from flask import render_template, request
from flask.ext.login import login_required, current_user
from flask.json import jsonify

import rfk.database
from rfk.site.helper import permission_required, emit_error
from rfk.database.show import Tag
from rfk.helper.taglist import taglist

from ..admin import admin



@admin.route('/tags')
@login_required
@permission_required(permission='admin')
def tags_list():
    tags = Tag.query.all()
    return render_template('admin/tags_list.html', tags=tags)


@admin.route('/tag/<int:tag>/edit')
@login_required
@permission_required(permission='admin')
def tags_edit(tag):
    tag = Tag.query.get(tag)
    if tag is None:
        return 'no tag found'
    if request.args.get('inline'):
        template = '/admin/tagform-inline.html'
    else:
        template = '/admin/tagform.html'
    return render_template(template, taglist=taglist, tag=tag)


@admin.route("/tag/<int:tag>/save", methods=['POST'])
@permission_required(permission='admin', ajax=True)
def save_tag(tag):
    tag = Tag.query.get(tag)
    if tag is None:
        return emit_error(1, 'Invalid Tag')
    tag.name = request.form['name']
    tag.description = request.form['description']
    tag.icon = request.form['icon']
    rfk.database.session.commit()
    return jsonify({'success': True, 'data': None})
