#!/usr/bin/env python

import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(basedir,'lib'))

import rfk
from rfk.database import init_db


rfk.init(basedir)
init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                               rfk.CONFIG.get('database', 'username'),
                                               rfk.CONFIG.get('database', 'password'),
                                               rfk.CONFIG.get('database', 'host'),
                                               rfk.CONFIG.get('database', 'database')))
import rfk.install

rfk.install.setup_permissions()
rfk.install.setup_settings()
rfk.install.setup_default_user('admin', 'admin')
rfk.database.session.commit()
