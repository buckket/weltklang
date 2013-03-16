from ConfigParser import SafeConfigParser
import os
import pygeoip


CONFIG = SafeConfigParser()

geoip = None

def init(basepath):
    global geoip
    CONFIG.read(os.path.join(basepath,'etc', 'config.cfg'))
    geoip = pygeoip.GeoIP(CONFIG.get('site', 'geoipdb'), pygeoip.MEMORY_CACHE)
