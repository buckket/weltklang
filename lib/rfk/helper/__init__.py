import pytz
import datetime
import rfk
import os
from flaskext.babel import lazy_gettext
from flask import url_for
from flask.helpers import find_package


def now():
    return pytz.utc.localize(datetime.datetime.utcnow())

def get_location(address):
    return rfk.geoip.record_by_addr(address)

def get_path(path='', internal=False):
    if os.path.isabs(path):
        return path
         
    prefix, package_path = find_package(__name__)
    if prefix is not None and not internal:
        return os.path.join(prefix, path)
    elif package_path is not None:
        return os.path.join(package_path, path)
    raise ValueError

def natural_join(lst):
    l = len(lst);
    if l <= 2:
        return lazy_gettext(' and ').join(lst)
    elif l > 2:
        first =  ', '.join(lst[0:-1])
        return "%s %s %s" % (first, lazy_gettext('and'), lst[-1])
    
def make_user_link(user):
    return '<a href="%s" title="%s">%s</a>' % (url_for('user.info',user=user.username),user.username,user.username);