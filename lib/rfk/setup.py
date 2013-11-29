#!/usr/bin/env python

import sys

import rfk
from rfk.database import init_db
import rfk.database


rfk.init()
if rfk.CONFIG.has_option('database', 'url'):
    init_db(rfk.CONFIG.get('database', 'url'))
else:
    init_db("%s://%s:%s@%s/%s" % (rfk.CONFIG.get('database', 'engine'),
                                  rfk.CONFIG.get('database', 'username'),
                                  rfk.CONFIG.get('database', 'password'),
                                  rfk.CONFIG.get('database', 'host'),
                                  rfk.CONFIG.get('database', 'database')))
import rfk.install

def main():
    rfk.install.setup_permissions()
    rfk.install.setup_settings()
    rfk.install.setup_default_user('admin', 'admin')
    rfk.database.session.commit()

if __name__ == '__main__':
    sys.exit(main())