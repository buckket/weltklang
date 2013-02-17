#!/usr/bin/python2.7

## too lazy to add pythonpath in env
import os
import sys
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(current_dir, 'lib/'))

import rfk
import rfk.database
import rfk.helper.daemonize
from rfk.liquidsoap.daemon import LiquidsoapDaemon

#import atexit

if __name__ == '__main__':
    rfk.helper.daemonize.createDaemon(current_dir)
    rfk.init(current_dir)
    rfk.database.init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                            rfk.CONFIG.get('database', 'username'),
                                                            rfk.CONFIG.get('database', 'password'),
                                                            rfk.CONFIG.get('database', 'host'),
                                                            rfk.CONFIG.get('database', 'database')))
    daemon = LiquidsoapDaemon(current_dir)
    