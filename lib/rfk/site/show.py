'''
Created on 16.05.2012

@author: teddydestodes
'''

from flask import Blueprint, render_template, url_for, request, redirect
from rfk.database.show import Show, Series
import rfk.database
from rfk import CONFIG
from rfk.site.forms.show import new_series_form
from flask.ext.login import login_required, current_user
import datetime


show = Blueprint('show',__name__)

@show.route('/shows/', defaults={'page':1})
@show.route('/shows/upcoming', defaults={'page':1})
@show.route('/shows/upcoming/<int:page>')
def upcoming(page):
    shows = Show.query.filter(Show.end > datetime.datetime.today()).all()
    return render_template('shows/upcoming.html', shows=shows)

@show.route('/show/<int:show>')
def view_show():
    return 'miep'

@show.route('/show/last')
def last():
    return 'blah'

@show.route('/check', methods=['POST'])
def check():
    pass

@show.route('/series')
def list_series():
    return 'null'

@show.route('/series/new', methods=["GET", "POST"])
@login_required
def new_series():
    form = new_series_form(request.form)
    if request.method == "POST" and form.validate():
        series = Series(user=current_user,
                        public=form.public.data,
                        name=form.name.data,
                        description=form.description.data,
                        logo=form.image.data)
        rfk.database.session.add(series)
        rfk.database.session.commit()
        return redirect(url_for('.list_series'))
    return render_template('shows/seriesform.html',form=form, imgur={'client': CONFIG.get('site', 'imgur-client'),
                                                           'secret': CONFIG.get('site', 'imgur-secret')})

@show.route('/series/<int:page>')
def view_series(series):
    return 'blah'

def create_menu(endpoint):
    menu = {'name': 'Programme', 'submenu': [], 'active': False}
    entries = [['show.upcoming', 'Upcomming Shows'],
               ['show.list_series', 'Series']]
    for entry in entries:
        active = endpoint == entry[0]
        menu['submenu'].append({'name': entry[1],
                                'url': url_for(entry[0]),
                                'active': (active)})
        if active:
            menu['active'] = True
    return menu

show.create_menu = create_menu