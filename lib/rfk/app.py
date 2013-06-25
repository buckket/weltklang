#!/usr/bin/python
'''
Created on 30.04.2012

@author: teddydestodes
'''
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

#monkeypatch "broken" babel lib
import flaskext.babel
import pytz
def to_utc(datetime):
    """Convert a datetime object to UTC [s]and drop tzinfo[/s].  This is the
    opposite operation to :func:`to_user_timezone`.
    """
    if datetime.tzinfo is None:
        datetime = flaskext.babel.get_timezone().localize(datetime)
    return datetime.astimezone(pytz.utc).replace(tzinfo=pytz.UTC)

flaskext.babel.to_utc = to_utc

import rfk
from rfk.database import init_db


rfk.init()
init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                               rfk.CONFIG.get('database', 'username'),
                                               rfk.CONFIG.get('database', 'password'),
                                               rfk.CONFIG.get('database', 'host'),
                                               rfk.CONFIG.get('database', 'database')))
from rfk.site import app
app.template_folder = '../templates/'
app.static_folder = '../static/'
app.static_url_path = '/static'


def main():
    app.run(host='0.0.0.0', debug=True)

if __name__ == '__main__':
    sys.exit(main())