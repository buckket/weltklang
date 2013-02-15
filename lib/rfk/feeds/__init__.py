from flask import Blueprint, g, request, jsonify
from datetime import datetime

import rfk.database
from rfk.database.base import User
from rfk.database.show import Show, UserShow

feeds = Blueprint('feeds', __name__)

def get_shows():
    clauses = []
    clauses.append(Show.end > datetime.utcnow())
    result = Show.query.join(UserShow).join(User).filter(*clauses).order_by(Show.begin.asc()).all()
    return result

from .ical import *
from .atom import *
