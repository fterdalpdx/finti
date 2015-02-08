import unittest
from flask.ext.testing import TestCase
from werkzeug.test import Client
from werkzeug.datastructures import Headers
from buildings_app.get_instance import app
from config import config
from redis import StrictRedis
import auth
import base64

class BuildingsAuthTest(TestCase):
	
	def create_app(self):
		app.config['TESTING'] = True
		self.client = app.test_client()
		return app
	
	
	def test_admin_page_is_locked(self):
		rv = self.client.get('/org/v1/buildings')

		self.assert_401(rv)
		self.assertTrue('WWW-Authenticate' in rv.headers)
		self.assertTrue('Basic' in rv.headers['WWW-Authenticate'])
	
	def test_admin_page_rejects_bad_username(self):
		h = Headers()
		h.add('Authorization', 'Basic ' + base64.b64encode('foo:my_password'))
		rv = Client.open(self.client, path='/org/v1/buildings',
						 headers=h)
		self.assert_403(rv)
	
	def test_admin_page_allows_valid_login(self):
		cache = StrictRedis(db=config.tokens_cache_redis_db)
		token = config.test_token
		token_hash = auth.calc_hash(token)
		cache.set(token_hash, 'test@test')
		h = Headers()
		h.add('Authorization',
			  'Basic ' + base64.b64encode(token + ':'))
		rv = Client.open(self.client, path='/org/v1/buildings',
						 headers=h)
		self.assert_200(rv)
		cache.delete(token_hash)
	
			
if __name__ == "__main__":
	unittest.main()	