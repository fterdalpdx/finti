'''
Created on Dec 31, 2014

@author: dennis
'''
import unittest
from lib.finti.oracle_model import Buildings as model

class Test(unittest.TestCase):


	def setUp(self):
		self.model = model()


	def tearDown(self):
		pass


	def ttest_list_buildings(self):
		buildings = self.model.list_buildings()
		self.assertTrue(len(buildings) > 40, 'more than a few buildings check')
		found_lh = False
		for building in buildings:
			if building['building_code'] == 'LH':
				found_lh = True
				self.assertTrue(building['zipcode'] == '97201', 'missing essential data check')
				self.assertTrue(building['street_address'] == '1620 SW PARK AVE', 'missing essential data check')
				self.assertTrue(building['state_code'] == 'OR', 'missing essential data check')
				self.assertTrue(building['city'] == 'Portland', 'missing essential data check')
				self.assertTrue(building['building_identifier'] == 'B0001', 'building identifier form check')
				print('LH: ' + repr(building))
		self.assertTrue(found_lh, 'obvious building check')
	
	def ttest_get_building_history(self):
		history = self.model.get_building_history('B0001')
		print('LH history: ' + repr(history))
		self.assertTrue(len(history) > 0, 'the first PSU building should have some history')
		
	def ttest_get_building(self):
		building = self.model.get_building('B0001')
		self.assertTrue(building['building_code'] == 'LH', 'lincoln hall better be lincoln hall')
		self.assertTrue(building['zipcode'] == '97201', 'missing essential data check')
		self.assertTrue(building['street_address'] == '1620 SW PARK AVE', 'missing essential data check')
		self.assertTrue(building['state_code'] == 'OR', 'missing essential data check')
		self.assertTrue(building['city'] == 'Portland', 'missing essential data check')
		self.assertTrue(building['building_identifier'] == 'B0001', 'building identifier form check')
		print('LH: ' + repr(building))
		
	def test_update_building(self):
		building = self.model.get_building('B0001')
		self.assertTrue(building['building_code'] == 'LH', 'lincoln hall better be lincoln hall')

		building['building_code'] = 'LHC'
		self.model.update_building(building)
		building['building_code'] = 'LH'
		self.model.update_building(building)
		

		
if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()