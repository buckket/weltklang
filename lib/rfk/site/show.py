'''
Created on 16.05.2012

@author: teddydestodes
'''

from flask import Blueprint, render_template, url_for
from rfk.database.show import Show
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

@show.route('/series/')
def list_series():
    return 'null'

@show.route('/series/<int:page>')
def view_series(series):
    return 'blah'

def create_menu():
    return {'name': 'Programme', 'submenu': [{'name': 'Upcomming Shows', 'url': url_for('show.upcoming')}]}

show.create_menu = create_menu