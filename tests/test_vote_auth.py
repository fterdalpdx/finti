import unittest
from flask.ext.testing import TestCase
from werkzeug.test import Client
from werkzeug.datastructures import Headers
from vote_app.get_instance import app
from config import config
from redis import StrictRedis
import auth
import base64

silence_all = False
test_name = 'bad_user'

class VoteAuthTest(TestCase):
	def setUp(self):
		cache = StrictRedis(db=config.tokens_cache_redis_db)
		token = config.test_token
		token_hash = auth.calc_hash(token)
		cache.set(token_hash, 'test@test')
		cache.sadd(config.people_scope_vote, 'test@test')

	def create_app(self):
		app.config['TESTING'] = True
		self.client = app.test_client()
		return app
	
	@unittest.skipIf(test_name <> 'locked' and silence_all==True, '')
	def test_vote_page_is_locked(self):
		rv = self.client.get('/people/v1/vote/foo')

		self.assert_401(rv)
		self.assertTrue('WWW-Authenticate' in rv.headers)
		self.assertTrue('Basic' in rv.headers['WWW-Authenticate'])
	
	@unittest.skipIf(test_name <> 'bad_user' and silence_all==True, '')
	def test_vote_page_rejects_bad_username(self):
		h = Headers()
		h.add('Authorization', 'Basic ' + base64.b64encode('foo:my_password'))
		rv = Client.open(self.client, path='/people/v1/vote/foo',
						 headers=h)
		self.assert_403(rv)
	
	@unittest.skipIf(test_name <> 'scope' and silence_all==True, '')
	def test_vote_page_check_scope(self):
		cache = StrictRedis(db=config.tokens_cache_redis_db)

		h = Headers()
		h.add('Authorization',
			  'Basic ' + base64.b64encode(config.test_token + ':'))
		rv = Client.open(self.client, path='/people/v1/vote/hhauer',
						 headers=h)
		self.assert_200(rv)
		
		cache.srem(config.people_scope_vote, 'test@test')

		rv = Client.open(self.client, path='/people/v1/vote/hhauer',
						 headers=h)
		self.assert_403(rv)
		cache.sadd(config.people_scope_vote, 'test@test')
		

		
	@unittest.skipIf(test_name <> 'valid_user' and silence_all==True, '')
	def test_vote_page_allows_valid_login(self):
		token = config.test_token
		h = Headers()
		h.add('Authorization',
			  'Basic ' + base64.b64encode(token + ':'))
		rv = Client.open(self.client, path='/people/v1/vote/hhauer',
						 headers=h)
		self.assert_200(rv)
		#cache.delete(token_hash)
	
			
if __name__ == "__main__":
	unittest.main()	