'''
Created on Jun 25, 2013

@author: teddydestodes
'''
import unittest

import rfk.database
from rfk.database.base import User
from rfk.database.show import Show, UserShow
import rfk.liquidsoaphandler

class Test(unittest.TestCase):

    def setUp(self):
        rfk.database.init_db('sqlite://', False)
        User.add_user('test', 'test')

    def tearDown(self):
        pass

    def test_do_connect(self):
        rfk.liquidsoaphandler.doConnect([])

    def test_do_metadata(self):
        rfk.liquidsoaphandler.doMetaData({"album": "{Awayland}", "userid": "3", "title": "{Awayland}", "vendor": "Xiph.Org libVorbis I 20101101 (Schaufenugget)", "artist": "Villagers"})

    def test_init_show_unplanned(self):
        user = User.get_user(username='test')
        show_name = 'testshow'
        show_description = 'testdescription'
        show_tags = 'tag tag1 tag2 tag3'
        show_logo = 'http://example.com/logo.png'
        show = rfk.liquidsoaphandler.init_show(user, show_name, show_description, show_tags)
        self.assertIs(Show.get_active_show(), show)
        self.assertIs(show.name, show_name)
        self.assertIs(show.description, show_description)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()