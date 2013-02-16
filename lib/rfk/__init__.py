from ConfigParser import SafeConfigParser
import os


CONFIG = SafeConfigParser()

def init(basepath):
    CONFIG.read(os.path.join(basepath,'etc', 'config.cfg'))
