'''
Created on Feb 5, 2015

@author: dennis
'''

from config import config
import logging.config
import redis
import daemon
from optparse import OptionParser
import ldap
import json
import ldap.modlist as modlist
from buildings_app.buildings import Buildings

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

		
	def ldif2list(self, ldif_list):
		buildings = []
		for proto_ldif in ldif_list:
			building = {}
			(dn, ldif) = proto_ldif[0]
			for key, value in ldif.items():
				building[key] = value[0]
			buildings.append(self.mapm(building))
			
		return buildings

	
	def get_building(self, building_identifier):
		return self.list_buildings(building_identifier=building_identifier)
	
	def list_buildings(self, building_identifier='*'):
		self.log.info('list_buildings(): starting')
		result_set = []
		try:
			self.connect_ldap()

			self.ldap_con.protocol_version = ldap.VERSION3
			base_dn = config.ldap_base
			#scope = ldap.SCOPE_ONELEVEL
			scope = ldap.SCOPE_SUBTREE
			ret_attrs = None
			
			ldap_result_id = self.ldap_con.search(base_dn, scope, 'buildingIdentifier=' + building_identifier, ret_attrs)
			
			while True:
				result_type, result_data = self.ldap_con.result(ldap_result_id,0)
				if (result_data == []):
					break
				else:
					if result_type == ldap.RES_SEARCH_ENTRY:
						result_set.append(result_data)
			
			self.log.info('list_buildings(): retrieved entry count: ' + str(len(result_set)))
			self.ldap_con.unbind_s()
		except ldap.LDAPError, ex:
			self.log.error('list_buildings(): failed to search LDAP: error: ' + str(ex))
		
		return self.ldif2list(result_set)
		
	def add_building(self, building):
		'''
			Add a new building. Transform a subset of building fields to the field names of the LDAP/AD schema.
		'''
		
		status = False
		try:
			self.log.info('add_building(): adding building: ' + building['building_code'] + " to LDAP")
			self.connect_ldap()
			dn = 'buildingIdentifier=' + building['building_identifier'] + ',' + config.ldap_base
			self.log.info('add_building(): adding building, dn: ' + dn)
			attrs = self.mapm(building)
			self.log.info('add_building(): attrs to add: ' + str(attrs))
			ldif = modlist.addModlist(attrs)
			self.log.info('add_building(): ldif to add: ' + str(ldif))
			self.ldap_con.add_s(dn, ldif)
			status = True
			self.log.debug('add_building(): ldif: ' + str(ldif))
			
			self.log.info('add_building(): successfully added building: ' + building['building_code'] + " to LDAP")
			self.ldap_con.unbind_s()
		except Exception as ex:
			self.log.error('add_buildings(): failed to add ' + building['building_code'] + ' to LDAP: error: ' + str(ex))
		
		return status


	def mapm(self, building):
		'''
			Translate a full building into the remapped subset for AD/LDAP and vice versa
		'''
		
		if 'building_code' in building:
			attrs = {
				"objectclass": 			str('psuBuilding'),
				"buildingCode": 		str(building['building_code']),
				"buildingIdentifier": 	str(building['building_identifier']),
				"buildingName": 		str(building['long_name']),
				"buildingShortName": 	str(building['short_name']),
				"street": 				str(building['street_address']),
				"l": 					str(building['city']),
				"st": 					str(building['state_code']),
				"postalCode": 			str(building['zipcode']),
				"labeledURI": 			str('geo:' + building['geolocate_lat'] + ',' + building['geolocate_long'])
			}
		else:
			attrs = {
				'building_code': 		building['buildingCode'],
				'building_identifier':	building['buildingIdentifier'],
				'long_name':			building['buildingName'],
				'short_name':			building['buildingShortName'],
				'street_address':		building['street'],
				'city':					building['l'],
				'state_code':			building['st'],
				'zipcode':				building['postalCode'],
				'geolocate_lat':		building['labeledURI'].split(':')[1].split(',')[0],
				'geolocate_long': 		building['labeledURI'].split(',')[1]
			}
		return attrs
	
	
	def modify_building(self, building_from, building_to=None):
		'''
			Change an existing building from the first argument, into the second
		'''
		status = False
		try:
			self.log.info('modify_building(): modifying building: ' + building_from['building_code'] + " in LDAP")
			self.connect_ldap()
			dn = 'buildingIdentifier=' + building_from['building_identifier'] + ',' + config.ldap_base
			self.log.info('modify_building(): modifying building, dn: ' + dn)
			
			if building_to == None:
				self.log.info('modify_building(): fetching building from web service: ' + building_from['building_identifier'])
				building_to = self.get_building(building_from['building_identifier'])[0]
				
			from_attrs = self.mapm(building_from)
			to_attrs = self.mapm(building_to)

			ldif = modlist.modifyModlist(from_attrs, to_attrs)
			if ldif <> []:	# Something has changed
				self.log.debug('modify_building(): ldif: ' + str(ldif))
				self.ldap_con.modify_s(dn, ldif)
			status = True
			self.log.info('modify_building(): successfully modified building: ' + building_from['building_code'] + " to LDAP")
			#self.ldap_con.unbind_s()
		except Exception as ex:
			self.log.error('modify_buildings(): failed to modify ' + building_from['building_code'] + ' in LDAP: error: ' + str(ex))
		
		return status
		
		
	def delete_building(self, building):
		'''
			Delete the given building from LDAP/AD
		'''
		status = False
		try:
			self.connect_ldap()
			self.log.info('delete_building(): deleting building from LDAP: ' + building['building_code'])
			dn = 'buildingIdentifier=' + building['building_identifier'] + ',' + config.ldap_base
			self.log.info('delete_building(): deleting building, dn: ' + dn)
			self.ldap_con.delete_s(dn)
			status = True
			self.ldap_con.unbind_s()
		except Exception as ex:
			self.log.error('delete_buildings(): failed to delete ' + building['building_code'] + ' from LDAP: error: ' + str(ex))
		return status
	
	def update_buildings(self):
		'''
			Update all of the buildings in LDAP to the current state from the source of building changes
		'''
		# Get the list of current buildings from the authoritative source
		building_ws = Buildings()
		cur_buildings = json.loads(building_ws.get_buildings()['message'])
		# Get the list of buildings in LDAP
		ldap_buildings = self.list_buildings()
		
		# Calculate the buildings to add to LDAP
		for building in cur_buildings:
			ws_bid = building['building_identifier']
			if [b for b in ldap_buildings if b['building_identifier'] == ws_bid] == []:
				self.log.info('update_buildings() adding building to LDAP: ' + str(building))
				self.add_building(building)
		
		# Calculate the buildings to delete from LDAP
		for building in ldap_buildings:
			ldap_bid = building['building_identifier']
			if [b for b in cur_buildings if b['building_identifier'] == ldap_bid] == []:
				self.log.info('update_buildings() removing building from LDAP: ' + str(building))
				self.delete_building(building)

		# Modify (update) all the buildings in LDAP
		for building in cur_buildings:
			self.modify_building(building)


	def listen(self):
		'''
			Listen for update requests via pubsub. Allows asynchronous updates to LDAP/AD from the
			incoming web services requests
		'''
		
		cache = redis.StrictRedis(db=config.buildings_cache_redis_db)
		self.log.debug('listen(): connected to cache')

		self.log.info('listen(): starting listener')
		pubsub = cache.pubsub()
		pubsub.subscribe([config.directory_pubsub_channel])
		self.log.info('listen(): subscribed to channel: ' + config.directory_pubsub_channel)
		
		for item in pubsub.listen():
			self.log.info('listen(): item detected: ' + str(item))
			value = str(item['data'])
			message_type = str(item['type'])
			if message_type <> 'message':	# only look at message, not un/subscribe events
				continue
			
			self.log.info('listen(): updating directory on case: ' + value)
			self.update_buildings()
	
			
					
if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	parser.add_option("-f", "--fore", dest="fore", action='store_true', default=False, help="Run as a foreground process instead of a daemon")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
		if options.fore:
			print '\033]0;BuildingDirAgent\a' 
			building_dir_agent = BuildingDirAgent()
			building_dir_agent.listen()
		else:
			with daemon.DaemonContext():
				building_dir_agent = BuildingDirAgent()
				building_dir_agent.listen()


