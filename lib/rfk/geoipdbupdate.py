#!/usr/bin/env python

import sys
import shutil
import urllib
import subprocess
import progressbar

import rfk


def main():
    rfk.init(enable_geoip=False)

    def download_progress(blocks_read, block_size, total_size):
        if blocks_read == 0:
            widgets = [progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
            download_progress.progress_bar = progressbar.ProgressBar(widgets=widgets, maxval=(total_size/block_size) + 1).start()
        download_progress.progress_bar.update(blocks_read)

    db_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'
    (file_name, headers) = urllib.urlretrieve(db_url, reporthook=download_progress)

    ret_val = subprocess.call(['gunzip', file_name])
    if ret_val == 0:
        shutil.move(file_name[:-3], rfk.CONFIG.get('site', 'geoipdb'))
    else:
        raise IOError


if __name__ == '__main__':
    sys.exit(main())
