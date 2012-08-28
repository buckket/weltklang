# -*- coding: utf-8 -*-
import telnetlib
import rfk
import os
from string import Template
from sqlalchemy import *


class LiquidInterface:
    
    timeout = 5000
    
    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = port
        
    def connect(self):
        self.conn = telnetlib.Telnet(self.host, self.port)

    def close(self):
        self.conn.close()
        
    def getSinks(self):
        return self._list(filter='input')
    
    def getSources(self):
        return self._list(filter='input')
    
    def getVersion(self):
        return self._executeCommand('version')
        
    def _list(self,filter=None):
        list = self._executeCommand('list')
        for line in list.splitlines():
            print line
    
    
    def _executeCommand(self, command):
        self.conn.write("%s\n" % command)
        ret = self.conn.read_until('END', self.timeout)
        return ret

def gen_script(session, dir):
    """generates liquidsoap script from templates
    """
    bin = os.path.join(dir,'bin')
    interface = os.path.join(bin, 'liquidsoap-handler.py')
    logfile = os.path.join(dir, 'var', 'log', 'liquidsoap.log')
    address = rfk.config.get('liquidsoap', 'address')
    port = rfk.config.get('liquidsoap', 'port')
    
    
    template_string = open(os.path.join(dir, 'var', 'liquidsoap', 'main.liq'),
                           'r').read()
    
    template = Template(template_string)
    config = template.substitute(address=address,
                        port=port,
                        logfile=logfile,
                        lastFM='',
                        script=interface)
    config += make_output(session, dir)
    return config


def make_lastfm():
    script = ''
    return script

def make_output(session, dir):
    script = u''
    streams = session.query(rfk.Stream).all()
    for stream in streams:
        if stream.type == rfk.Stream.TYPE_OGG:
            file = 'output_vorbis.liq'
        elif stream.type == rfk.Stream.TYPE_AACP:
            file = 'output_aacp.liq'
        elif stream.type == rfk.Stream.TYPE_MP3:
            file = 'output_mp3.liq'
        elif stream.type == rfk.Stream.TYPE_OPUS:
            file = 'output_opus.liq'
        else:
            continue
        template_string = open(os.path.join(dir, 'var', 'liquidsoap', file),
                           'r').read()
        template = Template(template_string)
        script += template.substitute(name=stream.name,
                                      description=stream.description,
                                      quality=stream.quality,
                                      host=rfk.config.get('icecast',
                                                          'internal-address'),
                                      port=rfk.config.get('icecast',
                                                          'port'),
                                      username=stream.username,
                                      password=stream.password,
                                      mount=stream.mountpoint,
                                      url=rfk.config.get('site', 'url'))
    return script