'''
Created on Sep 29, 2014

@author: dennis
'''
import unittest

from app import tokens
from config import config

class TokensTest(unittest.TestCase):
	def setUp(self):
		tokens.app.config['TESTING'] = True
		self.app = tokens.app.test_client()

	def tearDown(self):
		#os.close(self.db_fd)
		#os.unlink(buildings.app.config['DATABASE'])
		pass

	#@unittest.skip('weatherwax')
	def test_event_accept(self):
		rv = self.app.get('/erp/gen/1.0/token/0')
		self.assertTrue(rv.status_code == 200)

if __name__ == "__main__":
	unittest.main()