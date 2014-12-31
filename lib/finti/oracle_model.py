'''
Created on Sep 22, 2014

@author: dennis
'''

#from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
import os
#import pprint
from config import Properties
import logging.config
import redis
from beaver.transports.base_transport import json
import cx_Oracle


#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(prop.db_path, 'data.sqlite')
#app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

#db = SQLAlchemy(app)

class Buildings():
	buildings_cache = {}
	
	def __init__(self):
		self.prop = Properties()
		logging.config.dictConfig(self.prop.logging_conf_dict)
		self.log = logging.getLogger('model')
		if self.prop.buildings_cache_enabled == True:
			redis = redis.StrictRedis(db=self.prop.buildings_cache_redis_db)

	def cache_buildings(self, buildings):
		self.buildings_cache = {}
		self.log.debug('cache_buildings(): updating local cache of all buildings')
		
		for building in buildings:
			self.buildings_cache[building['building_identifier']] = building
			
	def conv_building(self, bldg):
		result = {	'building_identifier': bldg['ZGOBBLDG_BLDG_ID'],
			'long_name': bldg['ZGTVBLDG_LONG_DESC'],
			'short_name': bldg['ZGTVBLDG_SHORT_DESC'],
			'building_code': bldg['ZGTVBLDG_CODE'],
			'street_address': bldg['ZGOBBLDG_STREET_LINE1'],
			'city': bldg['ZGOBBLDG_CITY'],
			'state_code': bldg['ZGOBBLDG_STATE_CODE'],
			'zipcode': bldg['ZGOBBLDG_ZIP'],
			'rlis_lat': bldg['ZGOBBLDG_RLIS_LAT'],
			'rlis_long': bldg['ZGOBBLDG_RLIS_LONG'],
			'geolocate_lat': bldg['ZGOBBLDG_GEOLOCATE_LAT'],
			'geolocate_long': bldg['ZGOBBLDG_GEOLOCATE_LONG'],
			'centroid_lat': bldg['ZGOBBLDG_CENTROID_LAT'],
			'centroid_long': bldg['ZGOBBLDG_CENTROID_LONG'],
			'from_date': bldg['ZGTVBLDG_FROM_DATE'],
			'to_date': bldg['ZGTVBLDG_TO_DATE'],
		}
		#if bldg['ZGOBBLDG_BLDG_ID'] == 'B0001':
		#	print('conv_building(): raw building info: ' + str(bldg))
		return result
		
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
			if self.prop.buildings_cache_enabled == True and force_cache_refresh == False:
				self.log.debug('list_buildings(): global caching enabled')
				buildings_json = redis.get('buildings')
				if buildings_json is not None:
					buildings = json.loads(buildings_json)
					self.log.info('list_buildings(): global cache hit')
					return buildings
			else:
				self.log.debug('list_buildings(): global cache lookup disabled')
					
			dsn = cx_Oracle.makedsn(*self.prop.database_dsn)
			db = cx_Oracle.connect(self.prop.lms_login, self.prop.lms_password, dsn)
			cursor = db.cursor()
			call_cursor = cursor.var(cx_Oracle.CURSOR)
			
			cursor.callfunc('zgd_building.f_getBuildings', call_cursor, [])
			
			for building_raw in list(call_cursor.getvalue()):
				building_json = building_raw[0]
				building = json.loads(building_json)
				buildings.append(self.conv_building(building))
			
			# Set the local cache for buildings
			self.cache_buildings(buildings)
					
			if self.prop.buildings_cache_enabled == True:
				buildings_json = json.dumps(buildings)
				redis.set('buildings', buildings_json, ex=self.prop.buildings_cache_ttl)
				self.log.info('list_buildings(): set global cache')
	
		except Exception as ex:
			self.log.error('list_building(): error: ' + str(ex))
	
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

		building = []
		if building_identifier in self.buildings_cache:
			self.log.info('get_building(): cache miss')
			building = self.buildings_cache[building_identifier]
		else:
			# Get the buildings list with the side-effect of setting the buildings cache
			self.list_buildings(force_cache_refresh=True)
			building = self.buildings_cache[building_identifier]
			self.log.info('get_building(): found building')

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
			self.log.debug('get_building_history(): start')
					
			dsn = cx_Oracle.makedsn(*self.prop.database_dsn)
			db = cx_Oracle.connect(self.prop.lms_login, self.prop.lms_password, dsn)
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

		try:
			self.log.debug('update_building(): start')
					
			dsn = cx_Oracle.makedsn(*self.prop.database_dsn)
			db = cx_Oracle.connect(self.prop.lms_login, self.prop.lms_password, dsn)
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
						building['centroid_lat'],
						building['centroid_long'],
						building['rlis_lat'],
						building['rlis_long'],
						building['geolocate_lat'],
						building['geolocate_long'],
						building['building_identifier'],
						building['from_date'],
						building['to_date'],
				])

			cursor.callproc('zgd_building.p_insBldg', [building_desc])

			# Update the building caches
			self.list_buildings(force_cache_refresh=True)
								
		except Exception as ex:
			self.log.error('update_building(): error: ' + str(ex))
	
		self.log.info('update_building(): updated building: ' + str(building))
		
	def remove_building(self, building_identifier):
		'''
			Remove (deactivate) a building from the set of all PSU buildings
		
			@type	building_identifier: string
			@param  building_identifier: Identity of the building to remove
			@rtype None
			@return Nothing is returned
		'''
		# Update the to_date for the building to now.
			
	def update_building(self, building):
		'''
			Update a current building in the set of all PSU buildings
		
			@type	building_identifier: string
			@param  building_identifier: Identity of the building to update
			@rtype dict
			@return Dictionary containing building descriptor data
		'''

		try:
			self.log.debug('update_building(): start')
					
			dsn = cx_Oracle.makedsn(*self.prop.database_dsn)
			db = cx_Oracle.connect(self.prop.lms_login, self.prop.lms_password, dsn)
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
						building['centroid_lat'],
						building['centroid_long'],
						building['rlis_lat'],
						building['rlis_long'],
						building['geolocate_lat'],
						building['geolocate_long'],
						building['building_identifier'],
						building['from_date'],
						building['to_date'],
				])

			cursor.callproc('zgd_building.p_updBldg', [building_desc])

			# Update the building caches
			self.list_buildings(force_cache_refresh=True)
								
		except Exception as ex:
			self.log.error('update_building(): error: ' + str(ex))
	
		self.log.info('update_building(): updated building: ' + str(building))
