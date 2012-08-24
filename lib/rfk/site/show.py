'''
Created on 16.05.2012

@author: teddydestodes
'''

from flask import Blueprint, render_template
import rfk
from rfk.site import db

show = Blueprint('show',__name__)

@show.route('/')
@show.route('/upcoming')
def upcoming():
    return 'penis'

@show.route('/last')
def last():
    return 'blah'