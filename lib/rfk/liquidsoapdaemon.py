#!/usr/bin/env python

import sys

import argparse

import rfk
import rfk.database
from rfk.helper import get_path
import rfk.helper.daemonize
from rfk.liquidsoap.daemon import LiquidsoapDaemon, SocketExists


def main():
    parser = argparse.ArgumentParser(description='PyRfK Daemon for running Liquidsoap',
                                     epilog='Anyways this should normally not called manually')
    parser.add_argument('--foreground', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if not args.foreground:
        rfk.helper.daemonize.createDaemon(get_path())

    rfk.init()

    rfk.database.init_db("%s://%s:%s@%s/%s" % (rfk.CONFIG.get('database', 'engine'),
                                               rfk.CONFIG.get('database', 'username'),
                                               rfk.CONFIG.get('database', 'password'),
                                               rfk.CONFIG.get('database', 'host'),
                                               rfk.CONFIG.get('database', 'database')))
    try:
        daemon = LiquidsoapDaemon(rfk.CONFIG.get('liquidsoap-daemon', 'socket'))
        if args.debug:
            daemon.set_debug(args.debug)
        if args.foreground:
            daemon.enable_stdout()
        daemon.run()

    except SocketExists:
        print 'Socket is already there, maybe another instance running?'
    finally:
        rfk.database.session.rollback()
        rfk.database.session.remove()


if __name__ == '__main__':
    sys.exit(main())
