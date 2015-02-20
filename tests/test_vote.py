'''
Created on Sep 29, 2014

@author: dennis
'''
import unittest

#from vote_app.get_instance import app
from vote_app.vote import vote
from config import config

class VoteTest(unittest.TestCase):
	def setUp(self):
		#app.config['TESTING'] = True
		#self.app = app.test_client()
		pass

	def tearDown(self):
		#os.close(self.db_fd)
		#os.unlink(buildings.app.config['DATABASE'])
		pass

	#@unittest.skip('weatherwax')
	def test_verify_eligibility(self):
		#rv = self.app.get('/status')
		#self.assertTrue(rv.status_code == 200)
		self.assertTrue(vote.verify_eligibility('dennis') == {'success': {'voter': 'false'}})
		
if __name__ == "__main__":
	unittest.main()