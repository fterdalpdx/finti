'''
Created on Feb 5, 2015

@author: dennis
'''
import unittest
from directory_app.building_dir_agent import BuildingDirAgent

silence_all = False
test_name = 'modify'

class Test(unittest.TestCase):


	def setUp(self):
		self.bda = BuildingDirAgent()


	def tearDown(self):
		pass


	@unittest.skipIf(test_name <> 'connect' and silence_all==True, '')
	def test_connect_ldap(self):
		try:
			self.bda.connect_ldap()
		except Exception:
			pass

	@unittest.skipIf(test_name <> 'list' and silence_all==True, '')
	def test_list_buildings(self):
		buildings = self.bda.list_buildings()
		print('buildings: ' + str(buildings))
	
	@unittest.skipIf(test_name <> 'add_del' and silence_all==True, '')
	def test_add_del_building(self):
		new_bldg = {
		      "building_code" : "BLKS",
		      "centroid_lat" : "45.512101",
		      "from_date" : "2015-01-29",
		      "city" : "Portland",
		      "rlis_long" : "-122.685651",
		      "street_address" : "1831 SW PARK AVE",
		      "building_identifier" : "B0W0W",
		      "zipcode" : "97201",
		      "rlis_lat" : "45.511995",
		      "geolocate_lat" : "45.512034",
		      "long_name" : "Blackstone Residence Hall",
		      "short_name" : "Blackstone",
		      "centroid_long" : "-122.685693",
		      "geolocate_long" : "-122.685633",
		      "state_code" : "OR",
		      "to_date" : "2099-12-31"
		   }
		ldap_bld = self.bda.get_building("B0W0W")
		if ldap_bld <> []:
			self.bda.delete_building(new_bldg)
		self.assertTrue(self.bda.add_building(new_bldg))
		ldap_bld = self.bda.get_building("B0W0W")
		#self.assertTrue(ldap_bld["B0W0W"]['buildingIdentifier'] == "B0W0W")
		self.assertTrue(ldap_bld[0]['building_identifier'] == "B0W0W")
		self.assertTrue(self.bda.delete_building(new_bldg))
		
	@unittest.skipIf(test_name <> 'modify' and silence_all==True, '')
	def test_modify_building(self):
		new_bldg = {
		      "building_code" : "BLKS",
		      "centroid_lat" : "45.512101",
		      "from_date" : "2015-01-29",
		      "city" : "Portland",
		      "rlis_long" : "-122.685651",
		      "street_address" : "1831 SW PARK AVE",
		      "building_identifier" : "B0W0W",
		      "zipcode" : "97201",
		      "rlis_lat" : "45.511995",
		      "geolocate_lat" : "45.512034",
		      "long_name" : "Blackstone Residence Hall",
		      "short_name" : "Blackstone",
		      "centroid_long" : "-122.685693",
		      "geolocate_long" : "-122.685633",
		      "state_code" : "OR",
		      "to_date" : "2099-12-31"
		   }

		ldap_bld = self.bda.get_building("B0W0W")
		if ldap_bld <> []:
			self.assertTrue(self.bda.delete_building(new_bldg))

		self.assertTrue(self.bda.add_building(new_bldg))
		ldap_bld = self.bda.get_building("B0W0W")
			
		self.assertTrue(ldap_bld[0]['building_identifier'] == "B0W0W")
		#self.assertTrue(ldap_bld["B0W0W"]['buildingIdentifier'] == "B0W0W")
		old_bldg = new_bldg.copy()
		new_bldg["building_code"] = "DOGHAUS"
		self.assertTrue(self.bda.modify_building(old_bldg, new_bldg))
		ldap_bld = self.bda.get_building("B0W0W")
		#print('bowow: ' + str(ldap_bld))
		self.assertTrue(ldap_bld[0]['building_code'] == "DOGHAUS")
		
		self.assertTrue(self.bda.delete_building(new_bldg))

if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()