from flask import render_template, flash, request
from flaskext.babel import lazy_gettext

import rfk.database
from rfk.database.base import  ApiKey
from flask.ext.login import login_required, current_user
from rfk.site.forms.apikey import new_apikey_form
from ..user import user

@user.route('/<user>/apikeys', methods=['GET', 'POST'])
@login_required
def apikey_list(user):
    form = new_apikey_form(request.form)
    if request.method == 'POST' and form.validate():
        apikey = ApiKey(application=form.application.data,
                        description=form.description.data,
                        user=current_user)
        apikey.gen_key()
        rfk.database.session.add(apikey)
        rfk.database.session.commit()
        form.application.data = ''
        form.description.data = ''
        flash(lazy_gettext('Added Apikey'))
    apikeys = ApiKey.query.filter(ApiKey.user == current_user).all()
    return render_template('user/apikeys.html',apikeys=apikeys, form=form)