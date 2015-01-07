'''
Created on Dec 31, 2014

@author: dennis
'''
import unittest
from app.oracle_model import Buildings as model
from config import config

class Test(unittest.TestCase):


	def setUp(self):
		self.model = model()


	def tearDown(self):
		pass


	def test_list_buildings(self):
		buildings = self.model.list_buildings()
		#self.assertTrue(len(buildings) > 40, 'more than a few buildings check')
		found_lh = False
		for building in buildings:
			print('building: ' + str(building))
			if False and building['building_code'] == 'LH':
				found_lh = True
				self.assertTrue(building['zipcode'] == '97201', 'missing essential data check')
				self.assertTrue(building['street_address'] == '1620 SW PARK AVE', 'missing essential data check')
				self.assertTrue(building['state_code'] == 'OR', 'missing essential data check')
				self.assertTrue(building['city'] == 'Portland', 'missing essential data check')
				self.assertTrue(building['building_identifier'] == 'B0001', 'building identifier form check')
				print('LH: ' + repr(building))
		#self.assertTrue(found_lh, 'obvious building check')
	
	def test_get_building_history(self):
		history = self.model.get_building_history('TEST88')
		print('HEX history: ' + repr(history))
		self.assertTrue(len(history) > 0, 'the first PSU building should have some history')
		
		'''
		history = self.model.get_building_history('B0001')
		print('LH history: ' + repr(history))
		self.assertTrue(len(history) > 0, 'the first PSU building should have some history')
		'''
	def test_get_building(self):
		building = self.model.get_building('TEST88')
		self.assertTrue(building['building_code'] == 'HEX', 'Magic hall better be Magic hall')
		self.assertTrue(building['zipcode'] == '97225', 'missing essential data check')
		self.assertTrue(building['street_address'] == '8888 Broadway', 'missing essential data check')
		self.assertTrue(building['state_code'] == 'OR', 'missing essential data check')
		self.assertTrue(building['city'] == 'Ahnk-Morpork', 'missing essential data check')
		self.assertTrue(building['building_identifier'] == 'TEST88', 'building identifier form check')
		print('HEX: ' + repr(building))
		'''
		building = self.model.get_building('B0001')
		self.assertTrue(building['building_code'] == 'LH', 'lincoln hall better be lincoln hall')
		self.assertTrue(building['zipcode'] == '97201', 'missing essential data check')
		self.assertTrue(building['street_address'] == '1620 SW PARK AVE', 'missing essential data check')
		self.assertTrue(building['state_code'] == 'OR', 'missing essential data check')
		self.assertTrue(building['city'] == 'Portland', 'missing essential data check')
		self.assertTrue(building['building_identifier'] == 'B0001', 'building identifier form check')
		print('LH: ' + repr(building))
		'''
	@unittest.skip('not ready to update now')
	@unittest.skipIf(config.release_level == config.production, 'skipping modifying type unit-test against production')
	def test_update_building(self):
		building = self.model.get_building('B0001')
		self.assertTrue(building['building_code'] == 'LH', 'lincoln hall better be lincoln hall')

		building['building_code'] = 'LHC'
		self.model.update_building(building)
		building['building_code'] = 'LH'
		self.model.update_building(building)

	@unittest.skip('not ready to update now')
	@unittest.skipIf(config.release_level == config.production, 'skipping modifying type unit-test against production')
	def test_create_building(self):
		test_building = { 
			'long_name':		'High Energy Magic Building (TEST)',
			'short_name':		'Magic Building',
			'building_code': 	'HEX',
			'street_address': 	'8888 Broadway',
			'city':				'Ahnk-Morpork',
			'state_code': 		'OR',
			'zipcode': 			'97225',
			'centroid_lat': 	'45.508556',
			'centroid_long':	'-122.682755',
			'rlis_lat': 		'45.508556',
			'rlis_long':		'-122.682755',
			'geolocate_lat': 	'45.508556',
			'geolocate_long':	'-122.682755',
			'building_identifier':	'TEST88',
			'from_date':		'2015-01-01',
			'to_date':			'2016-01-01'
		}
		result = self.model.create_building(test_building)
		
if __name__ == "__main__":
	
	unittest.main()