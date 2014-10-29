'''
Created on Sep 29, 2014

@author: dennis
'''
import unittest

from finti import buildings
import tempfile
import os
import json

class BuildingsTest(unittest.TestCase):
	def setUp(self):
		self.db_fd, buildings.app.config['DATABASE'] = tempfile.mkstemp()
		buildings.app.config['TESTING'] = True
		self.app = buildings.app.test_client()
		buildings.init_db()


	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(buildings.app.config['DATABASE'])

	def test_get_buildings(self):
		buildings_json = self.app.get('/erp/gen/1.0/buildings').data
		buildings = json.loads(buildings_json)
		self.assertTrue(len(buildings) == 2)

	def test_get_building(self):
		
		# Test the positive case of finding an expected building via URI path
		EB_rv = self.app.get('/erp/gen/1.0/buildings/B0038')
		EB = json.loads(EB_rv.data)
		self.assertTrue(EB['street_address'] == '1930 SW FOURTH AVENUE')
		self.assertTrue(EB_rv.status_code == 200)
		
		# Test the positive case of finding an expected building via query string
		EB_rv = self.app.get('/erp/gen/1.0/buildings', query_string=dict(building_identifier='B0038'))
		print('EB_rv: ' + str(EB_rv.data))
		EB = json.loads(EB_rv.data)
		self.assertTrue(EB['street_address'] == '1930 SW FOURTH AVENUE')
		self.assertTrue(EB_rv.status_code == 200)
		
		# Test the case of not finding a building via URI path
		EB_rv = self.app.get('/erp/gen/1.0/buildings/0000038')
		self.assertTrue(EB_rv.status_code == 404)
		
		# Test the case of not finding a building via query string
		EB_rv = self.app.get('/erp/gen/1.0/buildings', query_string=dict(building_identifier='0000038'))
		self.assertTrue(EB_rv.status_code == 404)
		
	def test_add_building(self):
		# Test of complete and correctly formated building data add
		HEMB = {
			"long_name": "High Energy Magic Building",
			"longitude": -122.682749, 
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"latitude": 45.508593,
			"building_identifier": "B8888",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "97888" }		
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 200)
		HEMB_rv_data = json.loads(HEMB_rv.data)
		self.assertTrue(HEMB_rv_data['long_name'] == "High Energy Magic Building")
		
		# Test of duplicate data add
		HEMB = {
			"long_name": "High Energy Magic Building",
			"longitude": -122.682749, 
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"latitude": 45.508593,
			"building_identifier": "B8888",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "97888" }		
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 404)
		HEMB_rv_data = json.loads(HEMB_rv.data)
		
		# Test of malformed data add
		HEMB = {
			"long_name": "High Energy Magic Building",
			"longitude": -122.682749, 
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"building_identifier": "B8889",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "97888" }		
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 404)
		HEMB_rv_data = json.loads(HEMB_rv.data)

	def test_update_building(self):
		# Test positive case of update to an existing building
		HEMB = {
			"long_name": "High Energy Magic Building",
			"longitude": -122.682749, 
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"latitude": 45.508593,
			"building_identifier": "B888888",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "97888" }		
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
		
	def test_delete_building(self):
		# Test the deletion of an existing building
		
		HEMB = {
			"long_name": "High Energy Magic Building",
			"longitude": -122.682749, 
			"short_name": "Magic Bldg",
			"building_code": "HEMB",
			"latitude": 45.508593,
			"building_identifier": "888",
			"state_code": "OR",
			"city": "Ankh-Morpork",
			"street_address": "2000 SW 5TH AVE",
			"zipcode": "888" }		
		HEMB_rv = self.app.post('/erp/gen/1.0/buildings', data=json.dumps(HEMB), headers={'Content-type': 'application/json'} )
		self.assertTrue(HEMB_rv.status_code == 200)
		HEMB_rv_data = json.loads(HEMB_rv.data)
		self.assertTrue(HEMB_rv_data['zipcode'] == "888")

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