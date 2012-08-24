'''
Created on Aug 11, 2012

@author: teddydestodes
'''

from flask import Blueprint, render_template, g
import rfk
from rfk.site import db
from flask.ext.login import login_required

admin = Blueprint('admin',__name__)


@admin.route('/')
@login_required
def index():
    return render_template('admin/index.html')

@admin.route('/streams')
@login_required
def streams():
    return render_template('admin/streams.html')

@admin.route('/liquidsoap')
@login_required
def liquidsoap():
    return render_template('admin/streams.html')