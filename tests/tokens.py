'''
Created on Sep 29, 2014

@author: dennis
'''
import unittest

from tokens_app.get_instance import app
from config import config

class TokensTest(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()

	def tearDown(self):
		#os.close(self.db_fd)
		#os.unlink(buildings.app.config['DATABASE'])
		pass

	#@unittest.skip('weatherwax')
	def test_notify(self):
		rv = self.app.get('/erp/gen/1.0/token/0')
		self.assertTrue(rv.status_code == 200)

if __name__ == "__main__":
	unittest.main()