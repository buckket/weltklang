from flask import Blueprint, Flask, session, g, render_template, flash, redirect, url_for, request, jsonify


import rfk
from rfk.database import session
from rfk.database.base import User
from flask.ext.login import login_required, current_user
from rfk.site.forms.user import SettingsForm

from datetime import datetime

user = Blueprint('user',__name__)


@user.route('/', methods=['get'])
def list():
    users = User.query.all()
    return render_template('user/list.html', users=users, TITLE='User')


@user.route('/settings', methods=['get', 'post'])
@login_required
def settings():
    
    form = SettingsForm(request.form,
                        username=current_user.username,
                        email=current_user.mail,
                        show_def_name=current_user.get_setting(code='show_def_name'),
                        show_def_desc=current_user.get_setting(code='show_def_desc'),
                        show_def_tags=current_user.get_setting(code='show_def_tags'),
                        show_def_logo=current_user.get_setting(code='show_def_logo'),
                        use_icy=current_user.get_setting(code='use_icy'))
    
    if request.method == "POST" and form.validate():
        current_user.mail = form.email.data
        current_user.password = User.make_password(form.new_password.data)
        current_user.set_setting(code='show_def_name', value=form.show_def_name.data)
        current_user.set_setting(code='show_def_desc', value=form.show_def_desc.data)
        current_user.set_setting(code='show_def_tags', value=form.show_def_tags.data)
        current_user.set_setting(code='show_def_logo', value=form.show_def_logo.data)
        current_user.set_setting(code='use_icy', value=form.use_icy.data)
        session.commit()
        flash('Settings successfully updated')
        return redirect('user/settings')

    return render_template('user/settings.html', form=form, username=current_user.username, TITLE='User :: Settings')
    

@user.route('/<user>')
def info(user):
    user = User.get_user(username=user)
    if user:
        out = {}
        out['username'] = user.username
        #out['info'] = {'totaltime': user.get_stream_time(db.session)}
        #ushows = db.session.query(Show).join(UserShow).filter(UserShow.user==user, Show.begin > datetime.today()).order_by(Show.begin.asc())[:5]
        #lshows = db.session.query(Show).join(UserShow).filter(UserShow.user==user, Show.end <= datetime.today()).order_by(Show.end.desc())[:5]
        
        #out['shows'] = {'upcomming': ushows,
        #                'last': lshows
        #                }
        return render_template('user/info.html', username=user.username, info=out['info'], shows=out['shows'])
    else:
        return render_template('user/info.html', undefined=True)
