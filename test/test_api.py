import unittest

from flask import json

import rfk.exc
import rfk.database
from rfk.database.base import User
from rfk.database.base import ApiKey
from rfk.site import app


class PyRfKAPITest(unittest.TestCase):

    def setUp(self):
        rfk.init()
        rfk.database.init_db("sqlite://")

        app.template_folder = '../templates/'
        app.static_folder = '../static/'
        app.static_url_path = '/static'
        self.app = app.test_client()

        user_1 = User.add_user('teddydestodes', 'roflmaoblubb')
        user_2 = User.add_user('loom', 'bestes')

        key_1 = ApiKey(application='app_1', description='key_1', user=user_1)
        key_1.gen_key()
        self.key_1 = key_1.key
        key_2 = ApiKey(application='app_2', description='key_2', user=user_2, flag=ApiKey.FLAGS.DISABLED)
        key_2.gen_key()
        self.key_2 = key_2.key
        rfk.database.session.add(key_1, key_2)

        rfk.database.session.commit()

    def tearDown(self):
        rfk.database.session.remove()

    def is_valid_call(self, data):
        self.assertEqual(data['status']['code'], 0)
        self.assertEqual(data['status']['message'], None)

    def test_call_invalid_endpoint(self):
        rv = self.app.get('/api/web/invalid_endpoint')
        data = json.loads(rv.data)
        self.assertEqual(data['status']['code'], 404)
        self.assertEqual(data['status']['message'], "'invalid_endpoint' not found")

    def test_call_without_apikey(self):
        rv = self.app.get('/api/web/dj')
        data = json.loads(rv.data)
        self.assertEqual(data['status']['code'], 403)
        self.assertEqual(data['status']['message'], "api key missing")

    def test_call_with_invalid_apikey(self):
        rv = self.app.get('/api/web/dj?key=invalid')
        data = json.loads(rv.data)
        self.assertEqual(data['status']['code'], 403)
        self.assertEqual(data['status']['message'], "api key invalid")

    def test_call_with_disabled_apikey(self):
        rv = self.app.get('/api/web/dj?key=%s' % self.key_2)
        data = json.loads(rv.data)
        self.assertEqual(data['status']['code'], 403)
        self.assertEqual(data['status']['message'], "api key disabled")

    def test_dj(self):
        rv = self.app.get('/api/web/dj?key=%s' % self.key_1)
        data = json.loads(rv.data)
        self.assertEqual(data['status']['code'], 400)
        self.assertEqual(data['status']['message'], "missing required query parameter")

    def test_dj_with_dj_id(self):
        rv = self.app.get('/api/web/dj?dj_id=1&key=%s' % self.key_1)
        data = json.loads(rv.data)
        self.is_valid_call(data)
        self.assertDictEqual({'dj_id': 1, 'dj_name': 'teddydestodes'}, data['data']['dj'])

    def test_dj_with_invalid_dj_id(self):
        rv = self.app.get('/api/web/dj?dj_id=9000&key=%s' % self.key_1)
        data = json.loads(rv.data)
        self.is_valid_call(data)
        self.assertEqual(data['data']['dj'], None)

    def test_dj_with_dj_name(self):
        rv = self.app.get('/api/web/dj?dj_name=loom&key=%s' % self.key_1)
        data = json.loads(rv.data)
        self.is_valid_call(data)
        self.assertDictEqual({'dj_id': 2, 'dj_name': 'loom'}, data['data']['dj'])

    def test_dj_with_invalid_dj_name(self):
        rv = self.app.get('/api/web/dj?dj_name=invalid&key=%s' % self.key_1)
        data = json.loads(rv.data)
        self.is_valid_call(data)
        self.assertEqual(data['data']['dj'], None)


if __name__ == "__main__":
    unittest.main()
