'''
Created on Sep 29, 2014

@author: dennis
'''
import unittest

from buidings_app.get_instance import app
import json
from config import config
from requests.auth import HTTPBasicAuth

class BuildingsTest(unittest.TestCase):
	def setUp(self):
		#self.db_fd, buildings.app.config['DATABASE'] = tempfile.mkstemp()
		app.config['TESTING'] = True
		self.app = app.test_client()
		#buildings.init_db()


	def tearDown(self):
		#os.close(self.db_fd)
		#os.unlink(buildings.app.config['DATABASE'])
		pass

	#@unittest.skip('weatherwax')
	def test_get_buildings(self):
		buildings_json = self.app.get('/erp/gen/1.0/buildings').data
		buildings = json.loads(buildings_json)
		self.assertTrue(len(buildings) > 50)
		self.assertTrue('city' in buildings[0])
		self.assertTrue('long_name' in buildings[42])
		self.assertTrue('short_name' in buildings[17])
		self.assertTrue('building_identifier' in buildings[11])

	#@unittest.skip('back-end not ready yet')
	def test_get_building_history(self):
		building_history_json = self.app.get('/erp/gen/1.0/buildings/TEST88/history').data
		history = json.loads(building_history_json)
		self.assertTrue(len(history) > 1)
		
	#@unittest.skip('weatherwax')
	def test_get_building(self):

		# Test the positive case of finding an expected building via URI path
		EB_rv = self.app.get('/erp/gen/1.0/buildings/B0038')
		EB = json.loads(EB_rv.data)
		self.assertTrue(EB['street_address'] == '1930 SW FOURTH AVENUE')
		self.assertTrue(EB_rv.status_code == 200)

		# Test the positive case of finding an expected building via query string
		EB_rv = self.app.get('/erp/gen/1.0/buildings', query_string=dict(building_identifier='B0038'))
		#print('EB_rv: ' + str(EB_rv.data))
		EB = json.loads(EB_rv.data)
		self.assertTrue(EB['street_address'] == '1930 SW FOURTH AVENUE')
		self.assertTrue(EB_rv.status_code == 200)

		# Test the case of not finding a building via URI path
		EB_rv = self.app.get('/erp/gen/1.0/buildings/0000038')
		self.assertTrue(EB_rv.status_code == 404)

		# Test the case of not finding a building via query string
		EB_rv = self.app.get('/erp/gen/1.0/buildings', query_string=dict(building_identifier='0000038'))
		self.assertTrue(EB_rv.status_code == 404)

	@unittest.skip('weatherwax')
	@unittest.skipIf(config.release_level == config.production, 'skipping modifying type unit-test against production')
	def test_add_building(self):
		# Test of complete and correctly formated building data add
		HEMB = {
			"long_name": "High Energy Magic Building",
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"geolocate_lat": 45.508593,
			"geolocate_long": -122.682749, 
			"rlis_lat": 45.508593,
			"rlis_long": -122.682749, 
			"centroid_lat": 45.508593,
			"centroid_long": -122.682749, 
			"building_identifier": "B8888",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "97888",
			"from_date": "2010-01-01",
			"to_date": "2016-01-01"
		 }		
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 200)
		HEMB_rv_data = json.loads(HEMB_rv.data)
		self.assertTrue(HEMB_rv_data['long_name'] == "High Energy Magic Building")
		
		# Test of duplicate data add
		HEMB = {
			"long_name": "High Energy Magic Building",
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"geolocate_lat": 45.508593,
			"geolocate_long": -122.682749, 
			"rlis_lat": 45.508593,
			"rlis_long": -122.682749, 
			"centroid_lat": 45.508593,
			"centroid_long": -122.682749, 
			"building_identifier": "B8888",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "97888",
			"from_date": "2010-01-01",
			"to_date": "2016-01-01"
		}		
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 404)
		HEMB_rv_data = json.loads(HEMB_rv.data)
		
		# Test of malformed data add
		HEMB = {
			"long_name": "High Energy Magic Building",
			"geolocate_lat": 45.508593,
			"geolocate_long": -122.682749, 
			"rlis_lat": 45.508593,
			"rlis_long": -122.682749, 
			"centroid_lat": 45.508593,
			"_long": -122.682749, 
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"building_identifier": "B8889",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "97888", 
			"from_date": "2010-01-01",
			"to_date": "2016-01-01"
		}		
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 404)
		HEMB_rv_data = json.loads(HEMB_rv.data)

	@unittest.skip('weatherwax')
	def test_building_is_valid(self):
		HEMB = {
			"long_name": "High Energy Magic Building",
			"geolocate_lat": 45.508593,
			"geolocate_long": -122.682749, 
			"rlis_lat": 45.508593,
			"rlis_long": -122.682749, 
			"centroid_lat": 45.508593,
			"centroid_long": -122.682749, 
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"building_identifier": "B888888",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "97888", 
			"from_date": "2010-01-01",
			"to_date": "2016-01-01"
		}		

		# Check well-formed case
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 200)
		
		# Check additional field case
		HEMB_PLUS = HEMB
		HEMB_PLUS['another'] = 'field'
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB_PLUS), headers={'Content-type': 'application/json'} )
		self.assertFalse(HEMB_rv.status_code == 200)
		
		# Check missing field case
		HEMB_MINUS = HEMB
		del HEMB_MINUS['rlis_lat']
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB_MINUS), headers={'Content-type': 'application/json'} )
		self.assertFalse(HEMB_rv.status_code == 200)
		
		# Check type: non-numeric
		HEMB_NON_NUM = HEMB
		HEMB_NON_NUM["centroid_lat"] = 'abc'
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB_NON_NUM), headers={'Content-type': 'application/json'} )
		self.assertFalse(HEMB_rv.status_code == 200)
		
		# Check type: unicode
		HEMB_ASCII = HEMB
		HEMB_ASCII["city"] = 123
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB_ASCII), headers={'Content-type': 'application/json'} )
		self.assertFalse(HEMB_rv.status_code == 200)
		
		# Check null entries
		HEMB_NULL = HEMB
		HEMB_NULL["city"] = ''
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB_NULL), headers={'Content-type': 'application/json'} )
		self.assertFalse(HEMB_rv.status_code == 200)
		
		# Check entries too long
		HEMB_LONG = HEMB
		HEMB_LONG["city"] = 'asoethaoetuhsatoehuatoestnahseutasoehusaoehusaohsuathoeuthasoehusoaehuatohenahoesuhaonehunaohestn'
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB_LONG), headers={'Content-type': 'application/json'} )
		self.assertFalse(HEMB_rv.status_code == 200)
		
		# Check null entries too short
		HEMB_SHORT = HEMB
		HEMB_SHORT["city"] = ' '
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB_SHORT), headers={'Content-type': 'application/json'} )
		self.assertFalse(HEMB_rv.status_code == 200)
		
		
	@unittest.skip('weatherwax')
	@unittest.skipIf(config.release_level == config.production, 'skipping modifying type unit-test against production')
	def test_update_building(self):
		# Test positive case of update to an existing building

		HEMB = {
		   "geolocate_long" : -122.682755,
		   "zipcode" : "97225",
		   "building_code" : "XEH",
		   "to_date" : "2016-12-01",
		   "from_date" : "1888-12-02",
		   "rlis_lat" : 45.508556,
		   "rlis_long" : -122.682755,
		   "city" : "Ahnk-Morpork",
		   "centroid_lat" : 45.508556,
		   "geolocate_lat" : 45.508556,
		   "street_address" : "8888 Broadway",
		   "long_name" : "High Energy Magic Building TEST",
		   "centroid_long" : -122.682755,
		   "state_code" : "OR",
		   "short_name" : "Magic Building",
		   "building_identifier" : "TEST88"
		}

		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 200)
		HEMB_rv_data = json.loads(HEMB_rv.data)
		self.assertTrue(HEMB_rv_data['zipcode'] == "97888")
		
		HEMB['zipcode'] = '88888888'
		HEMB_rv = self.app.put('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 200)
		HEMB_rv_data = json.loads(HEMB_rv.data)
		self.assertTrue(HEMB_rv_data['zipcode'] == '88888888')
		
		# Test update to a non-existent building
		HEMB['building_identifier'] = '42'
		HEMB_rv = self.app.put('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 404)

	@unittest.skip('weatherwax')
	@unittest.skipIf(config.release_level == config.production, 'skipping modifying type unit-test against production')
	def test_delete_building(self):
		# Test the deletion of an existing building
		
		HEMB = {
			"long_name": "High Energy Magic Building",
			"geolocate_lat": 45.508593,
			"geolocate_long": -122.682749, 
			"rlis_lat": 45.508593,
			"rlis_long": -122.682749, 
			"centroid_lat": 45.508593,
			"centroid_long": -122.682749, 
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"building_identifier": "888",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "88888" }		
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 200)
		HEMB_rv_data = json.loads(HEMB_rv.data)
		self.assertTrue(HEMB_rv_data['zipcode'] == "88888")

		HEMB_rv = self.app.delete('/erp/gen/1.0/buildings/888')	# Delete the new building and check the result
		self.assertTrue(HEMB_rv.status_code == 200)
		self.assertTrue(HEMB_rv.data == "building removed")
		
		HEMB_rv = self.app.get('/erp/gen/1.0/buildings/888')	# Really check to see if the building is gone
		self.assertTrue(HEMB_rv.status_code == 404)
		
		# Test the deletion of a non-existent building
		
		HEMB_rv = self.app.delete('/erp/gen/1.0/buildings/080808')	# Delete the new building and check the result
		self.assertTrue(HEMB_rv.status_code == 404)
		
		
	
		
		


if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()