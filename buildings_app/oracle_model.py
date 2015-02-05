'''
Created on Sep 22, 2014

@author: dennis
'''

from config import config
import logging.config
import redis
import json
import cx_Oracle
import daemon
from optparse import OptionParser
import socket
import requests

class Buildings():
	
	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('model')
		self.log.info('init() connecting to local cache')
		self.cache = redis.StrictRedis(db=config.buildings_cache_redis_db)
		self.log.info('init() initializing cache entries')
		#self.update_caches()
			
	def update_cache(self):
		# Eliminate all cache data including deleted (inactive) buildings
		self.cache.flushdb()
		
		buildings = self.list_buildings()
		buildings_json = json.dumps(buildings)
		
		self.cache.set('buildings', buildings_json)
		self.log.info('update_caches(): updated buildings cache')

		for building in buildings:
			ident = building['building_identifier']
			code = building['building_code']
			building_json = json.dumps(building)
			self.cache.set(ident, building_json)
			self.cache.set(code, building_json)
									
	def no_update_caches(self):
		'''
			Update the cache for building(s). Buildings are cached by:
			all building list (single item), buildings by id, and buildings by code.
			Also update sibling caches
		'''
		
		self.log.info('update_caches(): regenerating caches')
		
		caches = {}
		for host in config.redis_hosts:
			try:
				cache = redis.StrictRedis(host=host, db=config.buildings_cache_redis_db, socket_connect_timeout=2) # dont block indefinitely
				cache.get('buildings')	# test connection to Redis
				caches[host] = cache
				self.log.info('update_caches(): connected to cache on host: ' + host)
			except:
				self.log.warn('update_caches(): cannot connect to Redis on host: ' + host)

		for cache in caches.values():
			cache.flushdb()	# Nuke all entries from orbit, it's the only way to be sure (eliminates deletes/deactivations).
			self.log.info('update_caches(): flushed db on host')

		buildings = self.list_buildings()
		buildings_json = json.dumps(buildings)
			
		for cache in caches.values():
			cache.set('buildings', buildings_json)
			self.log.info('update_caches(): updated buildings cache on host')

		for building in buildings:
			ident = building['building_identifier']
			code = building['building_code']
			building_json = json.dumps(building)
			# verify building to/from date is valid
			
			for cache in caches.values():
				cache.set(ident, building_json)
				cache.set(code, building_json)

	def notify_cache(self, cache_request):
		'''
			Receive notification of a user token change event. The notify method corresponds
			to the Observer design pattern 'notify' which is called by the 'subject'
		'''
		
		cache = redis.StrictRedis(db=config.buildings_cache_redis_db)
		self.log.debug('notify_cache(): connected to cache')

		try:
			self.log.info('notify_cache(): published notify item to pubsub queue')
			cache.publish(config.buildings_pubsub_channel, cache_request)
		except Exception as ex:
			self.log.error('notify_cache(): failed to publish to the ' + config.buildings_pubsub_channel +' queue, error: ' + str(ex))
	
				
	def conv_building(self, bldg):
		result = {	'building_identifier': bldg['ZGTVBLDG_ID'],
			'long_name': bldg['ZGTVBLDG_LONG_NAME'],
			'short_name': bldg['ZGTVBLDG_SHORT_NAME'],
			'building_code': bldg['ZGTVBLDG_BLDG_CODE'],
			'street_address': bldg['ZGTVBLDG_STREET_LINE1'],
			'city': bldg['ZGTVBLDG_CITY'],
			'state_code': bldg['ZGTVBLDG_STATE_CODE'],
			'zipcode': bldg['ZGTVBLDG_ZIP'],
			'rlis_lat': bldg['ZGTVBLDG_RLIS_LAT'],
			'rlis_long': bldg['ZGTVBLDG_RLIS_LONG'],
			'geolocate_lat': bldg['ZGTVBLDG_GEOLOCATE_LAT'],
			'geolocate_long': bldg['ZGTVBLDG_GEOLOCATE_LONG'],
			'centroid_lat': bldg['ZGTVBLDG_CENTROID_LAT'],
			'centroid_long': bldg['ZGTVBLDG_CENTROID_LONG'],
			'from_date': bldg['ZGTVBLDG_EFFECTIVE_DATE'],
			'to_date': bldg['ZGTVBLDG_END_DATE'],
		}
		#if bldg['ZGOBBLDG_BLDG_ID'] == 'B0001':
		#	print('conv_building(): raw building info: ' + str(bldg))
		return result
		
	def to_arrayvar(self, building_descriptor, cursor):
		ora_array = cursor.arrayvar(cx_Oracle.STRING, [
			building_descriptor['long_name'],
			building_descriptor['short_name'],
			building_descriptor['building_code'],
			building_descriptor['street_address'],
			building_descriptor['city'],
			building_descriptor['state_code'],
			building_descriptor['zipcode'],
			str(building_descriptor['centroid_lat']),
			str(building_descriptor['centroid_long']),
			str(building_descriptor['rlis_lat']),
			str(building_descriptor['rlis_long']),
			str(building_descriptor['geolocate_lat']),
			str(building_descriptor['geolocate_long']),
			building_descriptor['building_identifier'],
			building_descriptor['from_date'],
			building_descriptor['to_date']])
		return ora_array
	
	def list_buildings(self):
		'''
			List all current PSU buildings. Does not contain the building histories.
		
			@rtype list
			@return list of dictionaries containing building descriptor data
		'''
		buildings = []
		try:
			self.log.debug('list_buildings(): global caching enabled')
			buildings_json = self.cache.get('buildings')
			if buildings_json is not None:
				buildings = json.loads(buildings_json)
				self.log.info('list_buildings(): global cache hit')
				return buildings

			self.log.info('list_buildings(): global cache miss.')
					
			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
			call_cursor = cursor.var(cx_Oracle.CURSOR)
			
			cursor.callfunc('zgd_building.f_getBuildings', call_cursor, [])
			self.log.info('list_buildings(): looked-up building list from db')
			
			for building_raw in list(call_cursor.getvalue()):
				building_json = building_raw[0]
				#self.log.debug('list_buildings(): raw JSON data: ' + str(building_json))
				building = json.loads(building_json)
				buildings.append(self.conv_building(building))
			self.log.info('list_buildings(): transformed building list into normal form')
			db.close()

		except Exception as ex:
			self.log.error('list_building(): error: ' + str(ex))
		#finally:
	
		self.log.info('list_buildings(): returning list of buildings with length: ' + str(len(buildings)))
		return(buildings)

	def get_building(self, building_identifier):
		'''
			Lookup a current (active) building from the set of all PSU buildings. Does not provide the building history of changes
			
			TODO: This function should call the db proc function for the specific building, but until the oracle date issue is resolved, the results are indeterminate

			@type	building_identifier: string
			@param  building_identifier: unique identifier for a building
			@rtype dict
			@return Dictionary containing building descriptor data
		'''
		
		if building_identifier == config.buildings_refresh:
			self.notify_cache(config.buildings_echo)
			return {}
		
		self.log.info('get_building(): looking-up building with building_identifier: ' + building_identifier)
		building = None
		building_json = self.cache.get(building_identifier)
		if building_json is not None:
			building = json.loads(building_json)
			self.log.info('get_building(): cache hit')

		return building
		
	def get_building_history(self, building_id):
		'''
			Retrieve the change history for a specific building in the set of all PSU buildings
			The results of this call are not cached.
		
			@type	building_identifier: string
			@param  building_identifier: unique identifier for a building
			@rtype 	list
			@return list of dictionaries containing building descriptor data
		'''
		'''
		'''
		history = []
		try:
			self.log.debug('get_building_history(): fetching history for building: ' + building_id)
					
			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
			call_cursor = cursor.var(cx_Oracle.CURSOR)
			
			cursor.callfunc('zgd_building.f_getBuilding', call_cursor, [building_id, None])
			
			for building_raw in list(call_cursor.getvalue()):
				building_json = building_raw[0]
				building = json.loads(building_json)
				history.append(self.conv_building(building))
			
		except Exception as ex:
			self.log.error('get_building_history(): error: ' + str(ex))
	
		self.log.info('get_building_history(): returning list of building history with length: ' + str(len(history)))
		return(history)
	
	def add_building(self, building):
		'''
			Add a new building to the set of all PSU buildings
		
			@type	building: dict
			@param  building: Dictionary containing building descriptor data
			@rtype dict
			@return Dictionary containing building descriptor data
		'''
		is_success = False
		
		try:
			self.log.debug('add_building(): building_descriptor to add: ' + str(building))

			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
			call_cursor = cursor.var(cx_Oracle.CURSOR)
			building_desc = cursor.arrayvar(cx_Oracle.STRING, [
						building['long_name'],
						building['short_name'],
						building['building_code'],
						building['street_address'],
						building['city'],
						building['state_code'],
						building['zipcode'],
						str(building['centroid_lat']),
						str(building['centroid_long']),
						str(building['rlis_lat']),
						str(building['rlis_long']),
						str(building['geolocate_lat']),
						str(building['geolocate_long']),
						building['building_identifier'],
						building['from_date'],
						building['to_date'],
				])

			cursor.callproc('zgd_building.p_insBldg', [building_desc])
			self.log.info('add_building(): added building: ' + str(building))

			#self.update_cache()
			self.notify_cache(config.buildings_refresh)
			
			is_success = True
		except Exception as ex:
			self.log.critical('add_building(): failed to update DB for building: ' + str(building) + ', error: ' + str(ex))
	
		return is_success
		
			
	def update_building(self, building_descriptor):
		'''
			Update a current building in the set of all PSU buildings
		
			@type	building_descriptor: dict
			@param  building_descriptor: Identity of the building to update
			@rtype dict
			@return Dictionary containing building descriptor data
		'''

		is_success = False
		
		building_identifier = building_descriptor['building_identifier']
		cached_building = self.cache.get(building_identifier)
		if cached_building is None:
			self.log.info('update_building(): attempting to update a non-existent building: ' + building_identifier)
			return False
			
		try:
			self.log.debug('update_building(): updating building: ' + building_descriptor['building_identifier'])
					
			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
			#call_cursor = cursor.var(cx_Oracle.CURSOR)
			building_desc = cursor.arrayvar(cx_Oracle.STRING, [
						building_descriptor['long_name'],
						building_descriptor['short_name'],
						building_descriptor['building_code'],
						building_descriptor['street_address'],
						building_descriptor['city'],
						building_descriptor['state_code'],
						building_descriptor['zipcode'],
						str(building_descriptor['centroid_lat']),
						str(building_descriptor['centroid_long']),
						str(building_descriptor['rlis_lat']),
						str(building_descriptor['rlis_long']),
						str(building_descriptor['geolocate_lat']),
						str(building_descriptor['geolocate_long']),
						building_descriptor['building_identifier'],
						building_descriptor['from_date'],
						building_descriptor['to_date'],
				])

			cursor.callproc('zgd_building.p_updBldg', [building_desc])
			db.close()

			# Update the building caches
			#self.update_cache()
			self.notify_cache(config.buildings_refresh)
			
			is_success = True
		except Exception as ex:
			self.log.error('update_building(): error: ' + str(ex))
	
		self.log.info('update_building(): updated building: ' + str(building_descriptor))
		return(is_success)

	def listen(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('model')
		
		cache = redis.StrictRedis(db=config.buildings_cache_redis_db)
		self.log.debug('listen(): connected to cache')

		self.log.info('listen(): starting listener')
		pubsub = cache.pubsub()
		pubsub.subscribe([config.buildings_pubsub_channel])
		self.log.info('listen(): subscribed to channel: ' + config.buildings_pubsub_channel)

		myhostname = socket.gethostname()
		neighbors = [host for host in config.neighbors if host <> myhostname]
		self.log.info('listen(): neighbors are: ' + str(neighbors))
		
		for item in pubsub.listen():
			self.log.info('listen(): item detected: ' + str(item))
			value = str(item['data'])
			message_type = str(item['type'])
			if message_type <> 'message':
				continue
			
			is_echo = False
			if value.startswith('echo'):
				is_echo = True
				self.log.info('listen(): echo update detected: ' + value)
				
			self.log.info('listen(): updating cache on case: ' + value)

			self.update_cache()

			if is_echo == False:
				self.log.info('listen(): alerting neighbors of change')
				for neighbor in neighbors:
					try:
						requests.get('http://' + neighbor + ':8888/erp/gen/v1/buildings/' + config.buildings_refresh)
						self.log.info('listen(): alerted neighbor of change: ' + neighbor)
					except Exception:
						self.log.warn('listen() failed to contact neighbor: ' + neighbor)
						
				self.log.info('listen(): finished processing token change for item: ' + str(item['data']))

	
	
#model = Buildings()

if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	parser.add_option("-f", "--fore", dest="fore", action='store_true', default=False, help="Run as a foreground process instead of a daemon")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
		if options.fore:
			buildings = Buildings()
			print '\033]0;Buildings\a' 
			buildings.listen()
		else:
			with daemon.DaemonContext():
				buildings = Buildings()
				buildings.listen()


