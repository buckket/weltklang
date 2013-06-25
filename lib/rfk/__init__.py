from ConfigParser import SafeConfigParser
from flask.helpers import find_package
import os
import pygeoip


CONFIG = SafeConfigParser()

geoip = None

def init():
    global geoip
    prefix, package_path = find_package(__name__)
    print prefix, package_path
    config_locations = []
    if prefix is not None:
        config_locations.append(os.path.join(prefix, 'local','etc', 'rfk-config.cfg'))
        config_locations.append(os.path.join(prefix, 'etc', 'rfk-config.cfg'))
        config_locations.append(os.path.join(prefix, 'rfk-config.cfg'))
    if package_path is not None:
        config_locations.append(os.path.join(package_path, 'rfk', 'rfk-config.cfg'))
    succ_read = CONFIG.read(config_locations)
    geoip = pygeoip.GeoIP(CONFIG.get('site', 'geoipdb'), pygeoip.MEMORY_CACHE)
