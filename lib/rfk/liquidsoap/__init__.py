# -*- coding: utf-8 -*-
import telnetlib
import rfk
import os
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

def genScript(session, dir):
    
    bin = os.path.join(dir,'bin')
    liquidInterface = os.path.join(bin,'liquidsoap-handler.py')
    
    script  = "set('log.file.path','%s')\n" % os.path.join(dir,'var','log', 'liquidsoap.log')
    script += "set('log.stdout', true)\n"
    script += "set('server.telnet', true)\n"
    script += "set('harbor.bind_addr','%s')\n" % rfk.config.get('liquidsoap', 'address')
    
    script += """
def crossfade(a,b)
    add(normalize=false,
    [ sequence([ blank(duration=5.),
    fade.initial(duration=10.,b) ]),
    fade.final(duration=10.,a) ])
end
def next(j,a,b)
    add(normalize=false,[ sequence(merge=true,[ blank(duration=3.),
        fade.initial(duration=6.,b) ]),
        sequence([fade.final(duration=9.,a),
        j,fallback([])]) ])
end
def transition(j,a,b)
    add(normalize=false,[ fade.initial(b),sequence(merge=true,
        [blank(duration=1.),j,fallback([])]),
        fade.final(a) ])
end
def onfade(old, new)
    add([amplify(2.0,new), amplify(0.1, old)])
end

def outfade(old, new)
    add([new, old])
end
"""
    script += """
def auth(login,password) =
    ret = get_process_lines("%s auth #{quote(login)} #{quote(password)}")
    ret = list.hd(ret)
    bool_of_string(ret)
end

def live_start(mdata)
    ignore(system("%s connect #{quote(json_of(compact=true,mdata))}"))
end

def live_stop()
    ignore(test_process("%s disconnect"))
end

def writemeta(mdata)
    ignore(system("%s meta #{quote(json_of(compact=true,mdata))}"))
end
""" % (liquidInterface,liquidInterface,liquidInterface,liquidInterface)
    #script += makeRecordScript(dir)
    script += """
live = input.harbor(port= %s,on_connect = live_start, on_disconnect = live_stop, buffer=0., max = 10., auth = auth, "/live.ogg")

playlist = request.dynamic({ request.create("bar:foo", indicators= get_process_lines("%s playlist"))})
playlist = drop_metadata(playlist)
playlist = rewrite_metadata([("title","Kein Strömbernd")], playlist)
playlist = rewrite_metadata([("artist","Radio freies Krautchan")], playlist)
#playlist = mksave(playlist)

live = on_metadata(writemeta , live)
""" % (rfk.config.get('liquidsoap', 'port'),liquidInterface)
    script += makeLastFMScript()
    script += """
full = fallback(track_sensitive=false,transitions=[crossfade],[live,playlist])
"""
    script += makeOutput(session)
    return script


def makeRecordScript(dir):
    bin = os.path.join(dir,'bin')
    liquidInterface = os.path.join(bin,'liquidsoap-handler.py')
    script = """
def dump_closed(filename)
    # Tu irgendwas damit
    log("File \'#{filename}\' closed...")
    #ignore(system("%s finishrecord #{quote(filename)}"))
end

# A function to stop
# the current dump source
stop_f = ref (fun () -> ())
# You should make sure you never
# do a start when another dump
# is running.

# Start to dump
def start_dump(showid) =
    dump = fallback(track_sensitive=false,[live,blank()])
    dump = drop_metadata(dump)
    s = output.file(%%mp3.vbr(stereo=true, samplerate=44100, quality='%s', id3v2=true),
        on_start={log("Starting dump with id \'#{showid}\'")},
        on_close=dump_closed,
        fallible=true,
        reopen_delay=1.,
        append=true,
        id="recording",
        "/tmp/dump_#{showid}.mp3",
        dump)
    # We update the stop function
    stop_f := fun () -> source.shutdown(s)
end

# Stop dump
def stop_dump() =
    f = !stop_f
    f ()
end

# Some telnet/server command
server.register(namespace="dump",
                description="Start dumping.",
                usage="dump.start <showid>",
                "start",
                fun (s) -> begin start_dump(s) "Done!" end)
server.register(namespace="dump",
                description="Stop dumping.",
                usage="dump.stop",
                "stop",
                fun (s) -> begin stop_dump() "Done!" end)
""" % (liquidInterface, rfk.config.get('liquidsoap', 'recordquality'))
    return script

def makeLastFMScript():
    script = """
live = lastfm.submit.full(user="'.$_config['lastfm'][0].'", password="'.$_config['lastfm'][1].'", delay=0., force=true, live)
    """
    return script;

def makeOutput(session):
    script = ""
    streams = session.query(rfk.Stream).all()
    for stream in streams:
        print stream.type
        if stream.type == rfk.Stream.TYPE_OGG:
            script += makeOutputOGG(stream)
        elif stream.type == rfk.Stream.TYPE_AACP:
            script += makeOutputAACP(stream)
        elif stream.type == rfk.Stream.TYPE_MP3:
            script += makeOutputMP3(stream)
    return script

def makeOutputOGG(stream):
    script = """
%s=output.icecast(%%vorbis(samplerate=44100, channels=2, quality=0.%s),
                    host="%s",port=%s,protocol="http",
                    user="%s",password="%s",
                    mount="%s",
                    url="%s",public=false,
                    description="%s",
                    fallible=true,
                    full)
""" % (stream.name, stream.quality,
       rfk.config.get('icecast', 'internal-address'), rfk.config.get('icecast', 'port'),
       stream.username, stream.password,
       stream.mountpoint,
       rfk.config.get('site', 'url'),
       stream.description)
    return script

def makeOutputAACP(stream):
    script = """
%s=output.icecast(%%aacplus(channels=2, samplerate=44100, bitrate=%s),
                    host="%s",port=%s,protocol="http",
                    user="%s",password="%s",
                    mount="%s",
                    url="%s",public=false,
                    description="%s",
                    fallible=true,
                    full)
""" % (stream.name, stream.quality,
       rfk.config.get('icecast', 'internal-address'), rfk.config.get('icecast', 'port'),
       stream.username, stream.password,
       stream.mountpoint,
       rfk.config.get('site', 'url'),
       stream.description)
    return script
    return ''

def makeOutputMP3(stream):
    script = """
%s=output.icecast(%%mp3.vbr(stereo=true, samplerate=44100, quality=%s,id3v2=true),
                    host="%s",port=%s,protocol="http",
                    user="%s",password="%s",
                    mount="%s",
                    url="%s",public=false,
                    description="%s",
                    fallible=true,
                    full)
""" % (stream.name, stream.quality,
       rfk.config.get('icecast', 'internal-address'), rfk.config.get('icecast', 'port'),
       stream.username, stream.password,
       stream.mountpoint,
       rfk.config.get('site', 'url'),
       stream.description)
    return script