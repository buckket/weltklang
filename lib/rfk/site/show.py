'''
Created on 16.05.2012

@author: teddydestodes
'''

from flask import Blueprint, render_template, url_for, request
from rfk.database.show import Show
import datetime
show = Blueprint('show',__name__)
from rfk.site import app
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

@show.route('/series/')
def list_series():
    return 'null'

@show.route('/series/<int:page>')
def view_series(series):
    return 'blah'

def create_menu(endpoint):
    menu = {'name': 'Programme', 'submenu': [], 'active': False}
    entries = [['show.upcoming', 'Upcomming Shows']]
    for entry in entries:
        active = endpoint == entry[0]
        menu['submenu'].append({'name': entry[1],
                                'url': url_for(entry[0]),
                                'active': (active)})
        if active:
            menu['active'] = True
    return menu

show.create_menu = create_menu