# -*- coding: utf-8 -*-
import telnetlib
import rfk
import os
from string import Template
from rfk.database.streaming import Relay, Stream



class LiquidInterface(object):
    
    timeout = 5000
    
    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = port
        
    def connect(self):
        self.conn = telnetlib.Telnet(self.host, self.port)

    def close(self):
        self.conn.close()
        
    def get_sinks(self):
        sinks = []
        for item in self._list(filter='output'):
            sinks.append(LiquidSink(self, item[0], item[1]))
        return sinks
    
    def get_sources(self):
        sources = []
        for item in self._list(filter='input'):
            sources.append(LiquidSource(self, item[0], item[1]))
        return sources
    
    def get_status(self, sink_or_source):
        assert isinstance(sink_or_source, (LiquidSink, LiquidSource))
        return self.endpoint_action(sink_or_source.handler, 'status')
    
    def endpoint_action(self, handler, action):
        for line in self._execute_command("%s.%s" % (handler, action)).splitlines():
            if len(line) > 0:
                return line
    
    def get_version(self):
        for line in self._execute_command('version').splitlines():
            if len(line) > 0:
                return line
    
    def get_uptime(self):
        for line in self._execute_command('uptime').splitlines():
            if len(line) > 0:
                return line
    
    def kick_harbor(self):
        for source in self.get_sinks():
            if source.type == 'input.harbor':
                source.kick()
        
    def _list(self,filter=None):
        list = self._execute_command('list')
        for line in list.splitlines():
            spl = map(str.strip, line.split(':'))
            if len(spl) == 2 and (filter is None or spl[1].startswith('%s.' % (filter,))):
                yield spl
    
    
    def _execute_command(self, command):
        self.conn.write("%s\n" % command)
        ret = self.conn.read_until('END', self.timeout)
        return ret

class LiquidSink(object):
    
    def __init__(self, interface, handler, type):
        self.interface = interface
        self.handler = handler
        self.type = type
    
    def status(self):
        return self.interface.get_status(self)
    
    def __repr__(self):
        return "<rfk.liquidsoap.LiquidSink %s at %s>" % (self.type, self.handler)

class LiquidSource(object):
    
    def __init__(self, interface, handler, type):
        self.interface = interface
        self.handler = handler
        self.type = type
    
    def status(self):
        return self.interface.get_status(self)
    
    def kick(self):
        self.interface._execute_command("%s.kick" % (self.handler,))
    
    def __repr__(self):
        return "<rfk.liquidsoap.LiquidSource %s at %s>" % (self.type, self.handler)
    

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
            continue
            file = 'output_aacp.liq'
        elif stream.type == Stream.TYPES.MP3:
            file = 'output_mp3.liq'
        elif stream.type == Stream.TYPES.OPUS:
            continue
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