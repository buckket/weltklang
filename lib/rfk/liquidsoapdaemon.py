#!/usr/bin/python2.7

## too lazy to add pythonpath in env
import rfk
import sys
import argparse

import rfk.database
from rfk.helper import get_path
import rfk.helper.daemonize
from rfk.liquidsoap.daemon import LiquidsoapDaemon

#import atexit

def main():
    parser = argparse.ArgumentParser(description='PyRfK Interface for liquidsoap',
                                     epilog='Anyways this should normally not called manually')
    rfk.helper.daemonize.createDaemon(get_path())
    rfk.init()
    rfk.database.init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                            rfk.CONFIG.get('database', 'username'),
                                                            rfk.CONFIG.get('database', 'password'),
                                                            rfk.CONFIG.get('database', 'host'),
                                                            rfk.CONFIG.get('database', 'database')))
    daemon = LiquidsoapDaemon(get_path())

if __name__ == '__main__':
    sys.exit(main())
    