$name=output.icecast(%external(channels=2, samplerate=48000, process="opusenc --bitrate $quality - -"),
                    host="$host",port=$port,protocol="http",
                    user="$username",password="$password",
                    mount="$mount",
                    url="$url",public=false,
                    description="$description",
                    fallible=true,
                    full)
