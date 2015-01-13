'''
Created on Dec 31, 2014

@author: dennis
'''
import unittest
from app.oracle_model import model
from config import config

class Test(unittest.TestCase):


	def setUp(self):
		#self.model = model()
		pass


	def tearDown(self):
		pass

	#@unittest.skip('')
	def test_list_buildings(self):
		buildings = model.list_buildings()
		#self.assertTrue(len(buildings) > 40, 'more than a few buildings check')
		found_lh = False
		for building in buildings:
			#print('building: ' + str(building))
			if False and building['building_code'] == 'LH':
				found_lh = True
				self.assertTrue(building['zipcode'] == '97201', 'missing essential data check')
				self.assertTrue(building['street_address'] == '1620 SW PARK AVE', 'missing essential data check')
				self.assertTrue(building['state_code'] == 'OR', 'missing essential data check')
				self.assertTrue(building['city'] == 'Portland', 'missing essential data check')
				self.assertTrue(building['building_identifier'] == 'B0001', 'building identifier form check')
				#print('LH: ' + repr(building))
		#self.assertTrue(found_lh, 'obvious building check')
	
	#@unittest.skip('')
	#@unittest.expectedFailure
	def test_get_building_history(self):

		history = model.get_building_history('TEST88')
		print('HEX history: ' + repr(history))
		self.assertTrue(len(history) >= 2)
	
	#@unittest.skip('')
	#@unittest.expectedFailure
	def test_get_building(self):

		building = model.get_building('B0001')
		self.assertTrue(building['building_code'] == 'LH', 'lincoln hall better be lincoln hall')
		self.assertTrue(building['zipcode'] == '97201', 'missing essential data check')
		self.assertTrue(building['street_address'] == '1620 SW PARK AVE', 'missing essential data check')
		self.assertTrue(building['state_code'] == 'OR', 'missing essential data check')
		self.assertTrue(building['city'] == 'Portland', 'missing essential data check')
		self.assertTrue(building['building_identifier'] == 'B0001', 'building identifier form check')
		#print('LH: ' + repr(building))

	#@unittest.skip('not ready to update now')
	@unittest.skipIf(config.release_level == config.production, 'skipping modifying type unit-test against production')
	def test_update_building(self):
		building = model.get_building('TEST88')
		#self.assertTrue(building['building_code'] == 'HEX', 'HEM building better have a code of HEX')

		building['building_code'] = 'XEH'
		model.update_building(building)
		building = model.get_building('TEST88')
		self.assertTrue(building['building_code'] == 'XEH', 'HEM building better have a code of XEH')
		building['building_code'] = 'HEX'
		model.update_building(building)
		building = model.get_building('TEST88')
		self.assertTrue(building['building_code'] == 'HEX', 'HEM building better have a code of HEX again')

	@unittest.skip('not ready to update now')
	@unittest.skipIf(config.release_level == config.production, 'skipping modifying type unit-test against production')
	def test_add_building(self):
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
			'from_date':		'1888-12-02',
			'to_date':			'2016-12-01'
		}
		result = model.add_building(test_building)
				
if __name__ == "__main__":
	
	unittest.main()