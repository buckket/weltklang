from ConfigParser import SafeConfigParser
from flask.helpers import find_package
from rfk.exc.base import NoConfigException
import os
import geoip2.database


CONFIG = SafeConfigParser()

geoip = None

def init():
    global geoip
    prefix, package_path = find_package(__name__)
    config_locations = []
    if prefix is not None:
        config_locations.append(os.path.join(prefix, 'local','etc', 'rfk-config.cfg'))
        config_locations.append(os.path.join(prefix, 'etc', 'rfk-config.cfg'))
        config_locations.append(os.path.join(prefix, 'rfk-config.cfg'))
    if package_path is not None:
        config_locations.append(os.path.join(package_path, 'rfk', 'rfk-config.cfg'))
    succ_read = CONFIG.read(config_locations)
    if len(succ_read) == 0:
        raise NoConfigException()
    geoip = geoip2.database.Reader(CONFIG.get('site', 'geoipdb'))
