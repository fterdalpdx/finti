'''
Created on Sep 29, 2014

@author: dennis
'''
import unittest

from hold_app.hold import hold
from config import config

silence_all = False; test_name = 'clear'

class HoldTest(unittest.TestCase):
	def setUp(self):
		#app.config['TESTING'] = True
		#self.app = app.test_client()
		pass

	def tearDown(self):
		#os.close(self.db_fd)
		#os.unlink(buildings.app.config['DATABASE'])
		pass

	@unittest.skipIf(test_name <> 'clear' and silence_all==True, '')
	def test_clear_advising_hold(self):

		# Test authorized advisor with valid student
		hold_status = hold.clear_advising_hold(config.brano_psuid, config.hhauer_psuid)
		print(hold_status)
		self.assertTrue(hold_status == {'success': {'hold': 'cleared'}})
		
		# Test unauthorized advisor with valid student
		hold_status = hold.clear_advising_hold(config.dennis_psuid, config.hhauer_psuid)
		self.assertTrue(hold_status == {'success': {'hold': 'not authorized'}})
		
		# Test authorized advisor with not-existent student
		hold_status = hold.clear_advising_hold(config.brano_psuid, '0000')
		self.assertTrue('error' in hold_status and hold_status['error']['type'] == config.people_err_dne)
		
		# Test unauthorized advisor with valid student
		hold_status = hold.clear_advising_hold('0000', config.hhauer_psuid)
		self.assertTrue('error' in hold_status and hold_status['error']['type'] == config.people_err_dne)
		

	@unittest.skipIf(test_name <> 'auth' and silence_all==True, '')
	def test_verify_authorized(self):

		# Test authorized case
		hold_status = hold.verify_authorization(config.brano_psuid)
		self.assertTrue(hold_status == {'success': {'authorized': 'true'}})
		
		# Test unauthorized case
		hold_status = hold.verify_authorization(config.dennis_psuid)
		self.assertTrue(hold_status == {'success': {'authorized': 'false'}})
		
		# Test not-existent advisor
		hold_status = hold.verify_authorization('0000')
		self.assertTrue('error' in hold_status and hold_status['error']['type'] == config.people_err_dne)
		
	@unittest.skipIf(test_name <> 'hold' and silence_all==True, '')
	def test_get_advising_hold(self):

		# Test authorized case
		hold_status = hold.get_advising_hold(config.hhauer_psuid)
		self.assertTrue(hold_status == {'success': {'hold': 'true'}})
		
		# Test unauthorized case
		hold_status = hold.get_advising_hold(config.dennis_psuid)
		self.assertTrue(hold_status == {'success': {'hold': 'false'}})
		
		# Test not-existent advisor
		hold_status = hold.get_advising_hold('0000')
		self.assertTrue('error' in hold_status and hold_status['error']['type'] == config.people_err_dne)
		
		
		
if __name__ == "__main__":
	unittest.main()