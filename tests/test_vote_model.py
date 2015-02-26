'''
Created on Dec 31, 2014

@author: dennis
'''
import unittest
#from buildings_app.oracle_model import model
import vote_app.vote_model
from config import config
import time

silence_all = False
test_name = 'bad_user'

class Test(unittest.TestCase):


	def setUp(self):
		self.model = vote_app.vote_model.VoteModel()


	def tearDown(self):
		pass

	@unittest.skipIf(test_name <> 'verify' and silence_all==True, '')
	def test_verify_eligibilty(self):
		# Test eligible case
		
		is_eligible = self.model.verify_eligibility('hhauer')
		self.assertTrue(is_eligible == 'true')
		# Test ineligible case
		
		is_eligible = self.model.verify_eligibility('janaka')
		self.assertTrue(is_eligible == 'false')
		# Test non-existant user case
		
		is_eligible = self.model.verify_eligibility('rincewind_lumberjack')
		self.assertTrue(is_eligible == 'dne')
		
		# Verify the correct failure mode for oracle
		dsn = self.model.dsn
		self.model.dsn = 'foo'
		
		is_eligible = self.model.verify_eligibility('hhauer')
		self.assertTrue(is_eligible == 'db error')
		self.model.dsn = dsn	# Fix oracle 
		
		
if __name__ == "__main__":
	
	unittest.main()