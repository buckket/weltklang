from flask import Blueprint

api = Blueprint('api', __name__)

from .web import *
from .site import *
from .admin import *
from .locale_timezone import *
