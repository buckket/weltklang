from flask import Blueprint, g, request, jsonify

import rfk.helper
from rfk.helper import now

import rfk.database
from rfk.database.base import User
from rfk.database.show import Show, UserShow

import pytz

feeds = Blueprint('feeds', __name__)

def get_shows():
    clauses = []
    clauses.append(Show.end > now())
    result = Show.query.join(UserShow).join(User).filter(*clauses).order_by(Show.begin.asc()).all()
    return result

from .ical import *
from .atom import *
