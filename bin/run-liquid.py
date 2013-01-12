#!/usr/bin/python2.7
import rfk
import rfk.liquidsoap
import rfk.database
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import subprocess
from threading  import Thread
import atexit
import time

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

rfk.init(current_dir)
rfk.database.init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                               rfk.CONFIG.get('database', 'username'),
                                               rfk.CONFIG.get('database', 'password'),
                                               rfk.CONFIG.get('database', 'host'),
                                               rfk.CONFIG.get('database', 'database')))
process = None

def cleanup():
    if process.returncode == None:
        print 'shutting down liquidsoap'
        process.terminate()
        time.sleep(5)
        if process.returncode == None:
            print 'killing liquidsoap'
            process.kill()

if __name__ == '__main__':
    args = ['liquidsoap','-']
    atexit.register(cleanup)
    process = subprocess.Popen(args,bufsize=-1,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    print 'starting'
    print rfk.liquidsoap.gen_script(current_dir).encode('utf-8')
    print process.stdin.write(rfk.liquidsoap.gen_script(current_dir).encode('utf-8'))
    
    process.stdin.close()
    print 'started'
    while process.returncode == None:
        print process.stdout.readline()
        #print process.stderr.readline()
        process.poll()