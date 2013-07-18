'''
Created on Jun 25, 2013

@author: teddydestodes
'''
import unittest

import rfk.database
from rfk.database.base import User
from rfk.database.show import Show, UserShow
from rfk.database.track import Track
import rfk.liquidsoaphandler
from rfk.install import setup_settings
from rfk.helper import now
from datetime import timedelta

class Test(unittest.TestCase):

    def setUp(self):
        rfk.database.init_db('sqlite://', True)
        setup_settings()
        try:
            self.user = User.add_user('teddydestodes', 'roflmaoblubb')
            User.add_user('test', 'test')
        except UserNameTakenException:
            pass
        rfk.database.session.commit()

    def tearDown(self):
        rfk.database.session.remove()

    def test_do_connect_invalid_user(self):
        
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
        self.test_do_connect_valid_user()
        data = {"album": "Pedestrian Verse", "userid": "1", "title": "Late March, Death March", "vendor": "Xiph.Org libVorbis I 20101101 (Schaufenugget)", "artist": "Frightened Rabbit"}
        rfk.liquidsoaphandler.doMetaData(data)
        print Track.current_track()
    
    def test_init_show_planned(self):
        begin = now()-timedelta(minutes=10)
        end = now()+timedelta(minutes=10)
        show = Show(begin=begin,
                    end=end,
                    name='titel',
                    description='description',
                    flags=Show.FLAGS.PLANNED)
        rfk.database.session.add(show)
        rfk.database.session.flush()
        show.add_user(self.user)
        rfk.database.session.commit()
        self.test_do_connect_valid_user()
        self.assertEqual(show, show.get_active_show())
        
    
    def test_init_show_unplanned(self):
        pass
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()