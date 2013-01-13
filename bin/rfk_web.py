#!/usr/bin/python
'''
Created on 30.04.2012

@author: teddydestodes
'''
import os
import rfk
from rfk.database import init_db

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.init(current_dir)
    init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                               rfk.CONFIG.get('database', 'username'),
                                               rfk.CONFIG.get('database', 'password'),
                                               rfk.CONFIG.get('database', 'host'),
                                               rfk.CONFIG.get('database', 'database')))
    import rfk.site
    rfk.site.app.template_folder = os.path.join(current_dir,'var','template')
    rfk.site.app.static_folder = os.path.join(current_dir,'web_static')
    rfk.site.app.config['BABEL_LOCALE_PATH'] = os.path.join(current_dir,'var','translations')
    rfk.site.app.static_url_path = '/static'
    rfk.site.app.run(host='0.0.0.0', debug=True)