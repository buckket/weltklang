'''
Created on 16.05.2012

@author: teddydestodes
'''
from flask import Blueprint, render_template
import rfk
from rfk.site import db
from datetime import datetime

user = Blueprint('user',__name__)

@user.route('/', methods=['get'])
def list():
    users = db.session.query(rfk.User).all()
    return render_template('user/list.html', users=users)

@user.route('/<user>')
def info(user):
    user = db.session.query(rfk.User).filter(rfk.User.name == user).first()
    if user:
        
        out = {}
        out['username'] = user.name
        out['info'] = {'totaltime': user.get_stream_time(db.session)}
        ushows = db.session.query(rfk.Show).join(rfk.UserShow).join(rfk.User).filter(rfk.User.user==user.user, rfk.Show.begin > datetime.today()).order_by(rfk.Show.begin.asc())[:5]
        lshows = db.session.query(rfk.Show).join(rfk.UserShow).join(rfk.User).filter(rfk.User.user==user.user, rfk.Show.end <= datetime.today()).order_by(rfk.Show.end.desc())[:5]
        
        out['shows'] = {'upcomming': ushows,
                        'last': lshows
                        }
        return render_template('user/info.html', username=user.name, info=out['info'], shows=out['shows'])
    else:
        return render_template('user/info.html', undefined=True)