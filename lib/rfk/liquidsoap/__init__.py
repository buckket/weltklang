# -*- coding: utf-8 -*-
import telnetlib
import rfk
import os
from string import Template
from rfk.database.streaming import Relay, Stream



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

def gen_script(dir):
    """generates liquidsoap script from templates
    """
    bin = os.path.join(dir,'bin')
    interface = os.path.join(bin, 'liquidsoap-handler.py')
    logfile = os.path.join(dir, 'var', 'log', 'liquidsoap.log')
    address = rfk.CONFIG.get('liquidsoap', 'address')
    port = rfk.CONFIG.get('liquidsoap', 'port')
    
    
    template_string = open(os.path.join(dir, 'var', 'liquidsoap', 'main.liq'),
                           'r').read()
    
    template = Template(template_string)
    config = template.substitute(address=address,
                        port=port,
                        logfile=logfile,
                        lastFM='',
                        script=interface)
    if isinstance(config, str):
        config = config.decode('utf-8')
    if not isinstance(config, unicode):
        config = unicode(config)
    config += make_output(dir)
    return config


def make_lastfm():
    script = ''
    return script

def make_output(dir):
    script = u''
    streams = Stream.query.all()
    for stream in streams:
        if stream.type == Stream.TYPES.OGG:
            file = 'output_vorbis.liq'
        elif stream.type == Stream.TYPES.AACP:
            file = 'output_aacp.liq'
        elif stream.type == Stream.TYPES.MP3:
            file = 'output_mp3.liq'
        elif stream.type == Stream.TYPES.OPUS:
            file = 'output_opus.liq'
        else:
            continue
        template_string = open(os.path.join(dir, 'var', 'liquidsoap', file),
                           'r').read()
        template = Template(template_string)
        master = Relay.get_master()
        script += template.substitute(name=stream.code,
                                      description=stream.name,
                                      quality=stream.quality,
                                      host=master.address,
                                      port=master.port,
                                      username=master.auth_username,
                                      password=master.auth_password,
                                      mount=stream.mount,
                                      url=rfk.CONFIG.get('site', 'url'))
    if isinstance(streams, str):
        streams = streams.decode('utf-8')
    if not isinstance(streams, unicode):
        streams = unicode(streams)
    return script