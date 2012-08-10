#!/usr/bin/python
'''
Created on 30.04.2012

@author: teddydestodes
'''
import os
import rfk

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))
    import rfk.site
    #rfk.site.app.template_folder = os.path.join(current_dir,'var','template')
    rfk.site.app.run()