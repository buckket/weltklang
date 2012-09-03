'''
Created on 16.05.2012

@author: teddydestodes
'''
from flask import Blueprint, render_template
import rfk
from rfk.site import db
from datetime import datetime
from rfk.model import User, UserShow, Show
user = Blueprint('user',__name__)

@user.route('/', methods=['get'])
def list():
    users = db.session.query(User).all()
    return render_template('user/list.html', users=users)

@user.route('/<user>')
def info(user):
    user = db.session.query(User).filter(User.name == user).first()
    if user:
        
        out = {}
        out['username'] = user.name
        out['info'] = {'totaltime': user.get_stream_time(db.session)}
        ushows = db.session.query(Show).join(UserShow).filter(UserShow.user==user, Show.begin > datetime.today()).order_by(Show.begin.asc())[:5]
        lshows = db.session.query(Show).join(UserShow).filter(UserShow.user==user, Show.end <= datetime.today()).order_by(Show.end.desc())[:5]
        
        out['shows'] = {'upcomming': ushows,
                        'last': lshows
                        }
        return render_template('user/info.html', username=user.name, info=out['info'], shows=out['shows'])
    else:
        return render_template('user/info.html', undefined=True)