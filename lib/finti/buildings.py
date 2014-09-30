'''
Created on Sep 23, 2014

@author: dennis
'''
import model
import logging.config
from config import Properties
#from model import add_building, remove_building, list_buildings, update_building
from optparse import OptionParser
import daemon
import redis
from flask import Flask, jsonify, abort, make_response, request
import json
import traceback
import sys

class Buildings():
	'''
		Provides a model for the PSU buildings web service.
	'''

	def __init__(self):
		self.prop = Properties()
		logging.config.dictConfig(self.prop.logging_conf_dict)
		self.log = logging.getLogger('buildings')
		self.redis = redis.StrictRedis(db=self.prop.buildings_cache_redis_db)
		self.log.debug('__init__(): starting')
	
	def get_buildings(self):
		'''
			Get the listing of all buildings. First check the cache for a fresh copy, otherwise 
			go to the database and retrieve the listing, and cache afterward.
		'''
		result = {'status': 'error', 'result': ''}

		cached_get_buildings = self.redis.get('get_buildings')
		if cached_get_buildings is not None:
			self.log.debug('get_buildings(): cache hit')
			result = {'status': 'success', 'result': cached_get_buildings }
		else:
			buildings = model.list_buildings()
			if len(buildings) > 0:
				self.log.debug('get_buildings(): cache miss')
				buildings_json = json.dumps(buildings)
				self.redis.set('get_buildings', buildings_json, ex=self.prop.buildings_cache_ttl)
				result = {'status': 'success', 'result': buildings_json}
			else:
				self.log.error('get_buildings(): error: no buildings exist in model.')
				result['result'] = 'Request failed'
		return result
			
	# FIXME: Should use get parameters for input instead of requiring a JSON body
	def get_building(self, building_identifier):
		'''
			Get a single building by its building_identifier. First check the cache for a fresh copy, otherwise 
			go to the database and retrieve the entry, and cache afterward.
		'''
		result = {'status': 'error', 'result': ''}
		self.log.debug('get_building(): looking up building_identifier: ' + building_identifier)
		cached_get_building = self.redis.get(building_identifier)
		if cached_get_building is not None:
			self.log.debug('get_buildings(): cache hit')
			#building = json.loads(cached_get_building)
			result = {'status': 'success', 'result': cached_get_building }
		else:
			self.log.debug('get_building(): looking-up from database: building_identifier: ' + building_identifier)
			building = model.get_building(building_identifier)
			if not building is None:
				self.log.debug('get_building(): found in database, cache miss')
				building_json = json.dumps(building)
				self.redis.set(building_identifier, building_json, ex=self.prop.buildings_cache_ttl)
				result = {'status': 'success', 'result': building_json}
			else:
				self.log.warn('get_building(): error: building not found for building_identifier: ' + building_identifier)
				result = {'status': 'error', 'result': 'Building does not exist'}
		return result

	def building_is_valid(self, building_descriptor):
		'''
			Check if the provided building data is valid. At a minimum, check if all required fields are present
		'''
		
		try:
			#building = json.loads(building_json)
			required_fields = ['long_name', 'short_name', 'building_code', 'street_address', 'city',
							'state_code', 'zipcode', 'building_identifier', 'longitude', 'latitude']
			is_valid = True
			for field in required_fields:
				if not field in building_descriptor:
					self.log.info('building_is_valid(): missing building descriptor field: ' + field)
					is_valid = False
					break
			'''
			if is_valid == True:
				if 'location' in building:
					if not 'latitude' in building['location'] or not 'longitude' in building['location']:
						is_valid = False
			'''
		except Exception as ex:
			is_valid = False
		return(is_valid)	
		
	def create_building(self, building):
		'''
			Create a single building and add to the list of PSU buildings in the backing database. 
			Invalidate the cache of all buildings if there is an existing entry.  
		'''
		result = {'status': 'error', 'result': ''}

		if self.building_is_valid(building):
			if model.add_building(building) == True:
				self.log.debug('create_building(): successfully added a new building')
				self.redis.delete('get_buildings')	# Invalidate the 'get_buldings' cache
				self.redis.delete(building['building_identifier'])	# Invalidate the cache entry for a specific building
				result = {'status': 'success', 'result': 'successfully added a new building'}
			else:
				self.log.debug('create_building(): failed to add new building to database')
				result = {'status': 'error', 'result': 'failed to add new building to database'}
		else:
			self.log.debug('create_building(): building data is not valid')
			result = {'status': 'error', 'result': 'building data is not valid'}
		
		return(result)

	def update_building(self, building):
		'''
			Update a single building in the list of PSU buildings from the backing database. 
			Invalidate the cache of all buildings and also the specific building cache if there is an existing entry.  
		'''
		result = {'status': 'error', 'result': ''}

		if self.building_is_valid(building):
			if model.update_building(building) == True:
				self.log.debug('update_building(): successfully updated building: ' + str(building))
				self.redis.delete('get_buildings')	# Invalidate the 'get_buldings' cache
				self.redis.delete(building['building_identifier'])
				result = {'status': 'success', 'result': 'successfully updated a building'}
			else:
				self.log.debug('update_building(): failed to updated building in database')
				result = {'status': 'error', 'result': 'failed to update building in database'}
		else:
			self.log.debug('create_building(): building data is not valid')
			result = {'status': 'error', 'result': 'building data is not valid'}
		
		return(result)

	def delete_building(self, building_identifier):
		'''
			Delete an existing building and adjust the cache.
		'''
		result = {'status': 'error', 'result': ''}
		
		if model.remove_building(building_identifier) == True:
			self.log.info('delete_builiding(): removed building from model: building_identifier: ' + building_identifier)
			self.redis.delete('get_buildings')	# Invalidate the 'get_buldings' cache
			self.redis.delete(building_identifier)
			result = {'status': 'success', 'result': 'successfully deleted a building'}
		else:
			self.log.info('delete_builiding(): failed to remove building from model: building_identifier: ' + building_identifier)
			result = {'status': 'error', 'result': 'failed to delete a building: ' + building_identifier}
		return result

app = Flask(__name__)

'''
if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
	#	context = daemon.DaemonContext(umask=0o002)
	#	with context:
'''

buildings = Buildings()

app = Flask(__name__)

def init_db():
	model.init_db()
	
@app.route(buildings.prop.buildings_uri_path, methods = ['GET'])
def get_buildings():
	global buildings

	if request.args and 'building_identifier' in request.args:
		buildings.log.info('get_building(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
		building_identifier = request.args['building_identifier']

		result = buildings.get_building(building_identifier)
		if result['status'] <> 'success':
			abort(404, result['result'])
		else:
			return(make_response((result['result'], 200, {'Content-Type': 'application/json'})))

	else:
		buildings.log.info('get_buildings(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
		result = buildings.get_buildings()
		if result['status'] <> 'success':
			abort(400, result['result'])
		else:
			return(make_response((result['result'], 200, {'Content-Type': 'application/json'})))

@app.route(buildings.prop.buildings_uri_path + '/<building_identifier>', methods = ['GET'])
def get_building(building_identifier):
	global buildings
	
	result = buildings.get_building(building_identifier)
	if result['status'] <> 'success':
		abort(404, result['result'])
	else:
		return(make_response((result['result'], 200, {'Content-Type': 'application/json'})))

	

@app.route(buildings.prop.buildings_uri_path, methods = ['POST'])
def create_building():
	global buildings
	if request.json:
		buildings.log.info('create_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
		building_descriptor = request.json

		result = buildings.create_building(building_descriptor)
		if result['status'] <> 'success':
			buildings.log.info('create_building() handler: failed to create building: ' + result['result'])
			abort(404, result['result'])
			
		if result['status'] == 'success':
			buildings.log.info('create_building() handler: successfully created building: ' + result['result'])
			get_result = buildings.get_building(building_descriptor['building_identifier'])
			buildings.log.info('create_building() handler: looked-up created building: ' + str(get_result))
			if get_result['status'] == 'success':
				return(make_response((get_result['result'], 200, {'Content-Type': 'application/json'})))
			else:
				abort(400, 'Building inconsistency error.')
	else:
		abort(404, 'Building descriptor not valid.')
		
@app.route(buildings.prop.buildings_uri_path + '/<building_identifier>', methods = ['DELETE'])
def delete_building(building_identifier):
	global buildings

	buildings.log.info('delete_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))

	result = buildings.delete_building(building_identifier)
	if result['status'] <> 'success':
		buildings.log.info('delete_building() handler: failed to delete building: ' + result['result'])
		abort(404, result['result'])
	else:
		return('building removed')
		
@app.route(buildings.prop.buildings_uri_path, methods = ['PUT'])
def update_building():
	global buildings
	if request.json:
		buildings.log.info('update_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
		building_descriptor = request.json

		result = buildings.update_building(building_descriptor)
		if result['status'] <> 'success':
			buildings.log.info('update_building() handler: failed to update building: ' + result['result'])
			abort(404, result['result'])
			
		if result['status'] == 'success':
			buildings.log.info('update_building() handler: successfully updated building: ' + result['result'])
			get_result = buildings.get_building(building_descriptor['building_identifier'])
			buildings.log.info('update_building() handler: looked-up updated building: ' + str(get_result))
			if get_result['status'] == 'success':
				return(make_response((get_result['result'], 200, {'Content-Type': 'application/json'})))
			else:
				abort(404, 'Building inconsistency error.')
	else:
		abort(404, 'Building descriptor not valid.')
		

@app.errorhandler(400)
def custom_404(error):
	buildings.log.info('custom_400(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 400)

@app.errorhandler(404)
def custom_404(error):
	buildings.log.info('custom_404(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 404)




#app.run(host='0.0.0.0', debug = True)



		