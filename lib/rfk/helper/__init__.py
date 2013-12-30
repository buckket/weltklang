import pytz
import datetime
import rfk
import os
from flask.ext.babel import lazy_gettext
from flask import url_for
from flask.helpers import find_package
from posixpath import dirname


def now():
    return pytz.utc.localize(datetime.datetime.utcnow())


def get_location(address):
    location = rfk.geoip.record_by_addr(address)

    if 'city' in location and location['city'] is not None:
        location['city'] = location['city'].decode('latin-1').encode('utf-8')

    if 'country_code' in location and location['country_code'] is not None:
        if location['country_code'] == 'DE' and location['region_code'] == '02':
            location['country_code'] = 'BAY'
        elif location['country_code'] == 'US' and location['region_code'] == '48':
            location['country_code'] = 'TEX'

    return location


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
        first = ', '.join(lst[0:-1])
        return "%s %s %s" % (first, lazy_gettext('and'), lst[-1])


def make_user_link(user):
    return '<a href="%s" title="%s">%s</a>' % (url_for('user.info', user=user.username), user.username, user.username);


def iso_country_to_countryball(isocode):
    """returns the countryball for given isocode
    omsk if file not found"""
    if isocode is None:
        return 'unknown.png'
    isocode = isocode.lower()
    # rather dirty hack to get the path
    basepath = os.path.join(dirname(dirname(__file__)), 'static', 'img', 'cb')
    
    if rfk.CONFIG.has_option('site', 'cbprefix'):
        prebasepath = os.path.join(basepath, rfk.CONFIG.get('site', 'cbprefix'))
        if os.path.exists(os.path.join(prebasepath, '{}.png'.format(isocode))):
            return '{}{}.png'.format(rfk.CONFIG.get('site', 'cbprefix'),isocode)
        
    if os.path.exists(os.path.join(basepath, '{}.png'.format(isocode))):
        return '{}.png'.format(isocode)
    else:
        return 'unknown.png'
