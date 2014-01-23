#!/usr/bin/env python

import sys
import shutil
import urllib
import subprocess

import rfk


def main():
    rfk.init(enable_geoip=False)

    db_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'
    (file_name, headers) = urllib.urlretrieve(db_url)
    ret_val = subprocess.call(['gunzip', file_name])

    if ret_val == 0:
        shutil.move(file_name[:-3], rfk.CONFIG.get('site', 'geoipdb'))


if __name__ == '__main__':
    sys.exit(main())
