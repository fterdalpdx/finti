'''
Created on Dec 31, 2014

@author: dennis
'''
import unittest
#from buildings_app.oracle_model import model
#import hold_app.hold_model
import hold_app.hold_null_model
from config import config
import time

silence_all = True
test_name = 'auth'

class Test(unittest.TestCase):


	def setUp(self):
		#self.model = hold_app.hold_model.HoldModel()
		self.model = hold_app.hold_null_model.HoldNullModel()


	def tearDown(self):
		pass

	@unittest.skipIf(test_name <> 'auth' and silence_all==True, '')
	def test_verify_authorized(self):
		# Test authorized case
		
		is_authorized = self.model.verify_authorization(config.brano_psuid)
		self.assertTrue(is_authorized == 'true')
		
		# Test unauthorized case
		
		is_authorized = self.model.verify_authorization(config.dennis_psuid)
		self.assertTrue(is_authorized == 'false')

		# Test non-existent user case
		
		is_authorized = self.model.verify_authorization('0000')
		self.assertTrue(is_authorized == 'dne')
		
	@unittest.skipIf(test_name <> 'get_hold' and silence_all==True, '')
	def test_get_advising_hold(self):
		# Test has hold case
		
		has_hold = self.model.get_advising_hold(config.hhauer_psuid)
		self.assertTrue(has_hold == 'true')
		
		# Test does not have hold case
		
		has_hold = self.model.get_advising_hold(config.dennis_psuid)
		self.assertTrue(has_hold == 'false')

		# Test non-existent user case
		
		has_hold = self.model.get_advising_hold('0000')
		self.assertTrue(has_hold == 'dne')

	@unittest.skipIf(test_name <> 'clear' and silence_all==True, '')
	def test_clear_advising_hold(self):
		# Test clear hold with authorized advisor
		
		has_hold = self.model.clear_advising_hold(config.brano_psuid, config.hhauer_psuid)
		self.assertTrue(has_hold == 'success')
		
		# Test clear hold with unauthorized advisor
		
		has_hold = self.model.clear_advising_hold(config.dennis_psuid, config.hhauer_psuid)
		self.assertTrue(has_hold == 'not_authorized')

		# Test clear hold with non-existent advisor

		has_hold = self.model.clear_advising_hold('0000', config.hhauer_psuid)
		self.assertTrue(has_hold == 'dne')
		
		# Test clear hold with non-existent student
		
		has_hold = self.model.clear_advising_hold(config.brano_psuid, '0000')
		self.assertTrue(has_hold == 'dne')
		
		
if __name__ == "__main__":
	
	unittest.main()