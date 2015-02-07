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
			
			ldap_result_id = self.ldap_con.search(base_dn, scope, 'cn=*', ret_attrs)
			
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
		self.log.info('list_buildings(): starting')
		try:
			self.connect_ldap()
			dn = config.ldap_base
			attrs = {
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
			ldif = modlist.addModlist(attrs)
			
		except Exception as ex:
			self.log.error('add_buildings(): failed to add to LDAP: error: ' + str(ex))
		
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


