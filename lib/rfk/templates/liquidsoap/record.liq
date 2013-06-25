def dump_closed(filename)
    log("File \'#{filename}\' closed...")
    #ignore(system("$script finishrecord #{quote(filename)}"))
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
    s = output.file(%%mp3.vbr(stereo=true, samplerate=44100, quality='$quality', id3v2=true),
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