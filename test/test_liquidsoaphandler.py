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
        user = User.add_user('teddydestodes', 'roflmaoblubb')
        user.set_setting(False,code='use_icy')
        data = {"ice-public": "1",
                "ice-audio-info": "bitrate=128",
                "User-Agent": "libshout/2.3.1",
                "ice-url": " ",
                "ice-genre": "Live Mix",
                "ice-name": "Ohh Gott nicht der schonwieder",
                "ice-description": "waaaah",
                "Content-Type": "application/ogg",
                "Authorization": "Basic YWRtaW46YWRtaW4=W"}
        data = {"ice-public": "0",
         "ice-audio-info":
        "bitrate=128;samplerate=44100;channels=2",
        "User-Agent": "libshout/2.3.1",
        "ice-url": "http://www.example.com",
        "ice-genre": "Misc",
        "ice-name": "Herpderp",
        "ice-description": " ",
        "Content-Type": "application/ogg",
        "Authorization": "Basic dGVkZHlkZXN0b2Rlczpyb2ZsbWFvYmx1YmI="}

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