'''
Created on Feb 5, 2015

@author: dennis
'''

from config import config
import logging.config
import redis
import json
import daemon
from optparse import OptionParser
import socket
import ldap
import ldap.modlist as modlist

class BuildingDirAgent():
	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('building_dir_agent')
		self.log.info('init() connecting to local cache')
		self.cache = redis.StrictRedis(db=config.buildings_cache_redis_db)
		
	def connect_ldap(self):
		self.log.info('connect_ldap() connecting to: ' + config.ldap_url + ', with dn: ' + config.ldap_dn)

		ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
		self.ldap_con = ldap.initialize(config.ldap_url)
		self.ldap_con.set_option(ldap.OPT_REFERRALS, 0)
		self.ldap_con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
		self.ldap_con.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
		self.ldap_con.set_option( ldap.OPT_X_TLS_DEMAND, True )
		self.ldap_con.set_option( ldap.OPT_DEBUG_LEVEL, 255 )

		self.ldap_con.simple_bind_s(config.ldap_dn, config.ldap_password)
		self.log.info('connect_ldap() connected to: ' + config.ldap_url)
		
	def connect_ad(self):
		self.log.info('connect_ad() connecting to: ' + config.ad_url + ', with dn: ' + config.ad_dn)

		'''
		ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
		self.ldap_con = ldap.initialize(config.ldap_url)
		self.ldap_con.set_option(ldap.OPT_REFERRALS, 0)
		self.ldap_con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
		self.ldap_con.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
		self.ldap_con.set_option( ldap.OPT_X_TLS_DEMAND, True )
		self.ldap_con.set_option( ldap.OPT_DEBUG_LEVEL, 255 )
		'''
		self.ad_con = ldap.initialize(config.ad_url)
		self.ad_con.simple_bind_s(config.ad_dn, config.ad_password)
		self.log.info('connect_ad() connected to: ' + config.ad_url)
		
	def list_buildings(self):
		self.log.info('list_buildings(): starting')
		result_set = []
		try:
			self.connect_ldap()

			self.ldap_con.protocol_version = ldap.VERSION3
			base_dn = config.ldap_base
			#scope = ldap.SCOPE_ONELEVEL
			scope = ldap.SCOPE_SUBTREE
			ret_attrs = None
			
			ldap_result_id = self.ldap_con.search(base_dn, scope, 'buildingIdentifier=*', ret_attrs)
			
			while True:
				result_type, result_data = self.ldap_con.result(ldap_result_id,0)
				if (result_data == []):
					break
				else:
					if result_type == ldap.RES_SEARCH_ENTRY:
						result_set.append(result_data)
			
			self.log.info('list_buildings(): retrieved entry count: ' + str(len(result_set)))
						
		except ldap.LDAPError, ex:
			self.log.error('list_buildings(): failed to search LDAP: error: ' + str(ex))
		
		return result_set
		
	def add_building(self, building):
		status = False
		try:
			self.log.info('add_building(): adding building: ' + building['building_code'] + " to LDAP")
			self.connect_ldap()
			dn = 'buildingIdentifier=' + building['building_identifier'] + ',' + config.ldap_base
			self.log.info('add_building(): adding building, dn: ' + dn)
			attrs = {
				"ou": 'buildings',
				"buildingCode": building['building_code'],
				"buildingIdentifier": building['building_identifier'],
				"buildingName": building['long_name'],
				"buildingShortName": building['short_name'],
				"street": building['street_address'],
				"l": building['city'],
				"st": building['state_code'],
				"postalCode": building['zipcode'],
				"labeledURI": 'geo:' + building['geolocate_lat'] + ',' + building['geolocate_long']
			}
			ldif = [
				("objectclass", ['psuBuilding']),
				("buildingCode", [str(building['building_code'])]),
				("buildingIdentifier", [str(building['building_identifier'])]),
				("buildingName", [str(building['long_name'])]),
				("buildingShortName", [str(building['short_name'])]),
				("street", [str(building['street_address'])]),
				("l", [str(building['city'])]),
				("st", [str(building['state_code'])]),
				("postalCode", [str(building['zipcode'])]),
				("labeledURI", [str('geo:' + building['geolocate_lat'] + ',' + building['geolocate_long'])])
			]
			#ldif = modlist.addModlist(attrs)
			self.ldap_con.add_s(dn, ldif)
			status = True
			self.log.debug('add_building(): ldif: ' + str(ldif))
			
			self.log.info('add_building(): successfully added building: ' + building['building_code'] + " to LDAP")
		except Exception as ex:
			self.log.error('add_buildings(): failed to add ' + building['building_code'] + ' to LDAP: error: ' + str(ex))
		
		return status
	
	def delete_building(self, building):
		status = False
		try:
			self.connect_ldap()
			self.log.info('delete_building(): deleting building from LDAP: ' + building['building_code'])
			dn = 'buildingIdentifier=' + building['building_identifier'] + ',' + config.ldap_base
			self.log.info('add_building(): adding building, dn: ' + dn)
			self.ldap_con.delete_s(dn)
			status = True
		except Exception as ex:
			self.log.error('delete_buildings(): failed to delete ' + building['building_code'] + ' from LDAP: error: ' + str(ex))
	
if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	parser.add_option("-f", "--fore", dest="fore", action='store_true', default=False, help="Run as a foreground process instead of a daemon")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
		if options.fore:
			building_dir_agent = BuildingDirAgent()
			print '\033]0;BuildingDirAgent\a' 
			building_dir_agent.listen()
		else:
			with daemon.DaemonContext():
				building_dir_agent = BuildingDirAgent()
				building_dir_agent.listen()


