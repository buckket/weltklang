'''
Created on Jun 25, 2013

@author: teddydestodes
'''
import unittest

import rfk.database
from rfk.database.base import User
from rfk.database.show import Show, UserShow
import rfk.liquidsoaphandler
from rfk.install import setup_settings

class Test(unittest.TestCase):

    def setUp(self):
        rfk.database.init_db('sqlite://', False)
        setup_settings()

    def tearDown(self):
        pass

    def test_do_connect_invalid_user(self):
        User.add_user('test', 'test')
        data = {"ice-public": "1",
                "ice-audio-info": "bitrate=128",
                "User-Agent": "libshout/2.3.1",
                "ice-url": " ",
                "ice-genre": "Live Mix",
                "ice-name": "Ohh Gott nicht der schonwieder",
                "ice-description": "waaaah",
                "Content-Type": "application/ogg",
                "Authorization": "Basic YWRtaW46YWRtaW4=W"}
        rfk.liquidsoaphandler.doConnect(data)

    def test_do_connect_valid_user(self):
        User.add_user('admin', 'admin')
        data = {"ice-public": "1",
                "ice-audio-info": "bitrate=128",
                "User-Agent": "libshout/2.3.1",
                "ice-url": " ",
                "ice-genre": "Live Mix",
                "ice-name": "Ohh Gott nicht der schonwieder",
                "ice-description": "waaaah",
                "Content-Type": "application/ogg",
                "Authorization": "Basic YWRtaW46YWRtaW4=W"}
        rfk.liquidsoaphandler.doConnect(data)

    def test_do_metadata(self):
        data = {"ice-public": "1",
                "ice-audio-info": "bitrate=128",
                "User-Agent": "libshout/2.3.1",
                "ice-url": " ",
                "ice-genre": "Live Mix",
                "ice-name": "Ohh Gott nicht der schonwieder",
                "ice-description": "waaaah",
                "Content-Type": "application/ogg",
                "Authorization": "Basic YWRtaW46YWRtaW4=W"}

        rfk.liquidsoaphandler.doMetaData(data)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()