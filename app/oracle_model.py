'''
Created on Sep 22, 2014

@author: dennis
'''

#from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
import os
from config import config
import logging.config
import redis
from beaver.transports.base_transport import json
import cx_Oracle


#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(config.db_path, 'data.sqlite')
#app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

#db = SQLAlchemy(app)

class Buildings():
	buildings_cache = {}
	
	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('model')
		if config.buildings_cache_enabled == True:
			redis = redis.StrictRedis(db=config.buildings_cache_redis_db)

	def cache_buildings(self, buildings):
		self.buildings_cache = {}
		self.log.debug('cache_buildings(): updating local cache of all buildings')
		
		for building in buildings:
			self.buildings_cache[building['building_identifier']] = building
			
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
			building_descriptor['centroid_lat'],
			building_descriptor['centroid_long'],
			building_descriptor['rlis_lat'],
			building_descriptor['rlis_long'],
			building_descriptor['geolocate_lat'],
			building_descriptor['geolocate_long'],
			building_descriptor['building_identifier'],
			building_descriptor['from_date'],
			building_descriptor['to_date']])
		return ora_array
	
	def list_buildings(self, force_cache_refresh = False):
		'''
			List all current PSU buildings. Does not contain the building histories
		
			@type	force_cache_refresh: boolean 
			@param  force_cache_refresh: Optional parameter to force and cache a reload of all building data
			@rtype list
			@return list of dictionaries containing building descriptor data
		'''
		buildings = []
		try:
			if config.buildings_cache_enabled == True and force_cache_refresh == False:
				self.log.debug('list_buildings(): global caching enabled')
				buildings_json = redis.get('buildings')
				if buildings_json is not None:
					buildings = json.loads(buildings_json)
					self.log.info('list_buildings(): global cache hit')
					return buildings
			else:
				self.log.debug('list_buildings(): global cache lookup disabled')
					
			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
			call_cursor = cursor.var(cx_Oracle.CURSOR)
			
			cursor.callfunc('zgd_building.f_getBuildings', call_cursor, [])
			
			for building_raw in list(call_cursor.getvalue()):
				building_json = building_raw[0]
				#self.log.debug('list_buildings(): raw JSON data: ' + str(building_json))
				building = json.loads(building_json)
				buildings.append(self.conv_building(building))
			
			# Set the local cache for buildings
			self.cache_buildings(buildings)
					
			if config.buildings_cache_enabled == True:
				buildings_json = json.dumps(buildings)
				redis.set('buildings', buildings_json, ex=config.buildings_cache_ttl)
				self.log.info('list_buildings(): set global cache')
	
		except Exception as ex:
			self.log.error('list_building(): error: ' + str(ex))
		finally:
			db.close()
	
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
		
		self.log.info('get_building(): looking-up building with building_identifier: ' + building_identifier)
		building = []
		if building_identifier in self.buildings_cache:
			self.log.info('get_building(): cache hit')
			building = self.buildings_cache[building_identifier]
		else:
			# Get the buildings list with the side-effect of setting the buildings cache
			self.log.info('get_building(): cache miss')
			self.list_buildings(force_cache_refresh=True)
			if building_identifier in self.buildings_cache:
				self.log.info('get_building(): found building with building_identifier: ' + building_identifier)
				building = self.buildings_cache[building_identifier]
			else:
				self.log.info('get_building(): building does not exist. building_identifier: ' + building_identifier)
				building = None

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

			# Update the building caches
			self.list_buildings(force_cache_refresh=True)
			is_success = True
		except Exception as ex:
			self.log.error('add_building(): error: ' + str(ex))
	
		return is_success
		
	def remove_building(self, building_identifier):
		'''
			Remove (deactivate) a building from the set of all PSU buildings
		
			@type	building_identifier: string
			@param  building_identifier: Identity of the building to remove
			@rtype None
			@return Nothing is returned
		'''
		# Update the to_date for the building to now.
	
		
	def removeme_create_building(self, building_descriptor):
		'''
			Create a building and add to the set of all PSU buildings
		
			@type	building_descriptor: dict
			@param  building_descriptor: Information describing the building to create
			@rtype dict or None
			@return building_descriptor on success or None on failure
		'''

		try:
			return self.add_building(building_descriptor)
		
			self.log.debug('create_building(): t')
					
			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
			call_cursor = cursor.var(cx_Oracle.CURSOR)
			building_array = self.to_arrayvar(building_descriptor, cursor)
			#  INDEX BY BINARY_INTEGER: http://bytes.com/topic/python/answers/744211-cx_oracle-array-parameter
			#result = cursor.arrayvar(cx_Oracle.STRING, 16)

			# Following produces: error: ORA-06550: line 1, column 7: PLS-00306: wrong number or types of arguments in call to 'P_INSBLDG
			cursor.callproc('zgd_building.p_insBldg', [building_array])
			# Following produces: PLS-00306: wrong number or types of arguments in call to 'P_INSBLDG', ORA-06550: line 1, column 7: PL/SQL: Statement ignored
			cursor.callproc('zgd_building.p_insBldg', [
						building_descriptor['long_name'],
						building_descriptor['short_name'],
						building_descriptor['building_code'],
						building_descriptor['street_address'],
						building_descriptor['city'],
						building_descriptor['state_code'],
						building_descriptor['zipcode'],
						building_descriptor['centroid_lat'],
						building_descriptor['centroid_long'],
						building_descriptor['rlis_lat'],
						building_descriptor['rlis_long'],
						building_descriptor['geolocate_lat'],
						building_descriptor['geolocate_long'],
						building_descriptor['building_identifier'],
						building_descriptor['from_date'],
						building_descriptor['to_date'],
				])

			# Update the building caches
			self.list_buildings(force_cache_refresh=True)
								
		except Exception as ex:
			self.log.error('create_building(): error: ' + str(ex))
		finally:
			db.close()
	
		self.log.info('create_building(): created building: ' + str(building_descriptor))

			
	def update_building(self, building_descriptor):
		'''
			Update a current building in the set of all PSU buildings
		
			@type	building_descriptor: dict
			@param  building_descriptor: Identity of the building to update
			@rtype dict
			@return Dictionary containing building descriptor data
		'''

		is_success = False
		
		try:
			self.log.debug('update_building(): updating building: ' + building_descriptor['building_identifier'])
					
			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
			call_cursor = cursor.var(cx_Oracle.CURSOR)
			building_desc = cursor.arrayvar(cx_Oracle.STRING, [
						building_descriptor['long_name'],
						building_descriptor['short_name'],
						building_descriptor['building_code'],
						building_descriptor['street_address'],
						building_descriptor['city'],
						building_descriptor['state_code'],
						building_descriptor['zipcode'],
						building_descriptor['centroid_lat'],
						building_descriptor['centroid_long'],
						building_descriptor['rlis_lat'],
						building_descriptor['rlis_long'],
						building_descriptor['geolocate_lat'],
						building_descriptor['geolocate_long'],
						building_descriptor['building_identifier'],
						building_descriptor['from_date'],
						building_descriptor['to_date'],
				])

			cursor.callproc('zgd_building.p_updBldg', [building_desc])

			# Update the building caches
			self.list_buildings(force_cache_refresh=True)
			is_success = True
		except Exception as ex:
			self.log.error('update_building(): error: ' + str(ex))
		finally:
			db.close()
	
		self.log.info('update_building(): updated building: ' + str(building_descriptor))
		return(is_success)
	
	
model = Buildings()