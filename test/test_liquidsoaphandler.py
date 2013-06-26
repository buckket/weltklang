'''
Created on Jun 25, 2013

@author: teddydestodes
'''
import unittest

import rfk.database
from rfk.database.base import User
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
        rfk.liquidsoaphandler.doMetaData([])

    def test_init_show_unplanned(self):
        user = User.get_user(username='test')
        rfk.liquidsoaphandler.init_show(user, 'testshow', 'testdesctiption', 'testtag tag tag')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()