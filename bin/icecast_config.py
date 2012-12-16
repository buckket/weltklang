from rfk.icecast import IcecastConfig, Mount

if __name__ == '__main__':
    
    conf = IcecastConfig()
    conf.hostname = 'rfk-master'
    conf.address = '192.168.122.222'
    mogg = Mount()
    mogg.mount = '/radio.ogg'
    conf.mounts.append(mogg)
    print conf.get_xml()