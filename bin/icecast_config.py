from rfk.icecast import IcecastConfig

if __name__ == '__main__':
    
    conf = IcecastConfig()
    print conf.get_xml()