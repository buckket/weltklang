set('log.file.path','/home/teddydestodes/src/PyRfK/var/log/liquidsoap.log')
set('log.stdout', true)
set('server.telnet', true)
set('harbor.bind_addr','192.168.2.104')

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

def auth(login,password) =
    ret = get_process_lines("/home/teddydestodes/src/PyRfK/bin/liquidsoap-handler.py auth #{quote(login)} #{quote(password)}")
    ret = list.hd(ret)
    bool_of_string(ret)
end

userid = ref "none"

def append_userid(mdata) =
  [("userid",!userid)]
end

def live_start(mdata)
    ret = get_process_lines("/home/pyrfk/bin/liquidsoap-handler.py connect #{quote(json_of(compact=true,mdata))}")
    ignore(userid := list.hd(ret))
end

def live_stop()
    ignore(test_process("/home/pyrfk/bin/liquidsoap-handler.py disconnect #{quote(json_of(compact=true,!userid))}"))
    ignore(userid := "none")
end

def writemeta(mdata)
    ignore(system("/home/teddydestodes/src/PyRfK/bin/liquidsoap-handler.py meta #{quote(json_of(compact=true,mdata))}"))
end

live = input.harbor(port= 8080,on_connect = live_start, on_disconnect = live_stop, buffer=0., max = 10., auth = auth, "/live.ogg")

playlist = request.dynamic({ request.create("bar:foo", indicators= get_process_lines("/home/teddydestodes/src/PyRfK/bin/liquidsoap-handler.py playlist"))})
playlist = drop_metadata(playlist)
playlist = rewrite_metadata([("title","Kein Strömbernd")], playlist)
playlist = rewrite_metadata([("artist","Radio freies Krautchan")], playlist)
#playlist = mksave(playlist)

live = map_metadata(append_userid,live)
live = on_metadata(writemeta , live)

live = lastfm.submit.full(user="'.$_config['lastfm'][0].'", password="'.$_config['lastfm'][1].'", delay=0., force=true, live)
    
full = fallback(track_sensitive=false,transitions=[crossfade],[live,playlist])

MP3=output.icecast(%mp3.vbr(stereo=true, samplerate=44100, quality=4,id3v2=true),
                    host="192.168.2.104",port=8000,protocol="http",
                    user="source",password="krautkanal",
                    mount="/radio.mp3",
                    url="radio.krautchan.net",public=false,
                    description="RfK MP3",
                    fallible=true,
                    full)

OPUS=output.icecast(%external(channels=2, samplerate=48000, process="opusenc --music --bitrate 32 - -"),
                    host="192.168.2.104",port=8000,protocol="http",
                    user="source",password="krautkanal",
                    mount="/radio.opus",
                    url="radio.krautchan.net",public=false,
                    description="RfK OPUS",
                    format="audio/ogg",
                    fallible=true,
                    full)
