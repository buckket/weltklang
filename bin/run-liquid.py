#!/usr/bin/python2.7
import rfk
import rfk.liquidsoap
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import subprocess
from threading  import Thread
import atexit
import time

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))

engine = create_engine("%s://%s:%s@%s/%s?charset=utf8" % (rfk.config.get('database', 'engine'),
                                                          rfk.config.get('database', 'username'),
                                                          rfk.config.get('database', 'password'),
                                                          rfk.config.get('database', 'host'),
                                                          rfk.config.get('database', 'database')))
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
    Session = sessionmaker(bind=engine)
    session = Session()
    atexit.register(cleanup)
    process = subprocess.Popen(args,bufsize=-1,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    print 'starting'
    print process.stdin.write(rfk.liquidsoap.gen_script(session, current_dir).encode('utf-8'))
    
    process.stdin.close()
    print 'started'
    while process.returncode == None:
        print process.stdout.readline()
        #print process.stderr.readline()
        process.poll()
    
    session.close()