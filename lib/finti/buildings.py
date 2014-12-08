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
from flask import Flask, jsonify, abort, make_response, request
import json
import traceback
import sys
from boto.ec2.instancestatus import Status
import re

class Buildings():
	'''
		Encapsulates a model for the PSU buildings web service.
	'''

	def __init__(self):
		self.prop = Properties()
		logging.config.dictConfig(self.prop.logging_conf_dict)
		self.log = logging.getLogger('buildings')
		self.log.debug('__init__(): starting')
	
	def get_buildings(self):
		'''
			Get the listing of all buildings. First check the cache for a fresh copy, otherwise 
			go to the database and retrieve the listing, and cache afterward.
		'''
		status = {'result': 'error', 'message': ''}

		buildings = model.list_buildings()
		if len(buildings) > 0:
			buildings_json = json.dumps(buildings)
			status = {'result': 'success', 'message': buildings_json}
		else:
			self.log.error('get_buildings(): error: no buildings exist in model.')
			status['message'] = 'Request failed'
		return status
			
	# FIXME: Should use get parameters for input instead of requiring a JSON body
	def get_building(self, building_identifier):
		'''
			Get a single building by its building_identifier. First check the cache for a fresh copy, otherwise 
			go to the database and retrieve the entry, and cache afterward.
		'''
		status = {'result': 'error', 'message': ''}
		if not building_identifier.isalnum():
			status = {'result': 'error', 'message': 'invalid building_identifier: identifier is not an alphanumeric'}
			self.log.debug('get_building(): ' + status['message'])
			return(status)
			
		self.log.debug('get_building(): looking up building_identifier: ' + building_identifier)

		self.log.debug('get_building(): looking-up from database: building_identifier: ' + building_identifier)
		building = model.get_building(building_identifier)
		if not building is None:
			self.log.debug('get_building(): found in database, cache miss')
			building_json = json.dumps(building)
			status = {'result': 'success', 'message': building_json}
		else:
			self.log.warn('get_building(): error: building not found for building_identifier: ' + building_identifier)
			status = {'result': 'error', 'message': 'Building does not exist'}
		return status

	def building_is_valid(self, building_descriptor):
		'''
			Check if the provided building data is valid. At a minimum, check if all required fields are present
		'''
		status = {'result': 'success', 'message': 'building descriptor is valid'}
		alphanumspace_re = re.compile('[^a-zA-Z0-9-_., ]')
		self.log.debug('building_is_valid(): building_descriptor: ' + str(building_descriptor))
		
		try:
			if type(building_descriptor) is not dict:		# Is the structure of the building descriptor the correct type
				status = {'result': 'error', 'message': 'invalid building descriptor'}
				self.log.warn('building_is_valid(): ' + str(status))
				return(status)

			for field, constraint in self.prop.required_fields.items():
				if not field in building_descriptor:		# Is there a missing required field
					status =  {'result': 'error', 'message': 'building_descriptor missing required field: ' + field}
					self.log.warn('building_is_valid(): ' + str(status))
					return(status)
				if constraint['type'] is float:
					if type(building_descriptor[field]) is not float:	# Is the location coordinate not a floating point number.
						status = {'result': 'error', 'message': 'field: ' + field + ' is not a floating point number value'}
						self.log.warn('building_is_valid(): ' + str(status))
						return(status)
				if constraint['type'] is unicode:
					if (not type(building_descriptor[field]) is unicode) and (not type(building_descriptor[field]) is str):	# Is the text field text
						status = {'result': 'error', 'message': 'field: ' + field + ' is not a string or unicode value'}
						self.log.warn('building_is_valid(): ' + str(status))
						return(status)
					if len(building_descriptor[field]) > constraint['max_len']:		# Is the text field too long
						status = {'result': 'error', 'message': 'field: ' + field + ' is longer than ' + str(constraint['max_len']) + ' characters'}
						self.log.warn('building_is_valid(): ' + str(status))
						return(status)
					if len(building_descriptor[field]) < constraint['min_len']:		# Is the text field too long
						status = {'result': 'error', 'message': 'field: ' + field + ' is shorter than ' + str(constraint['min_len']) + ' characters'}
						self.log.warn('building_is_valid(): ' + str(status))
						return(status)
					if alphanumspace_re.search(building_descriptor[field]) is not None:		# Is the text field not alpha numeric with spaces and punctuation
						status = {'result': 'error', 'message': 'field: ' + field + ' contains non-alphanumeric/punctuation/white space characters ' + str(constraint['min_len']) + ' characters'}
						self.log.warn('building_is_valid(): ' + str(status))
						return(status)
			if len(building_descriptor.keys()) <> len(self.prop.required_fields):	# Is there any extra data 
				status = {'result': 'error', 'message': 'building_descriptor has extraneous fields'}
				self.log.warn('building_is_valid(): ' + str(status))
				return(status)
				
		except Exception as ex:
			status = {'result': 'error', 'message': str(ex)}

		self.log.debug('building_is_valid(): status: ' + str(status))
		
		return(status)	
		
	def create_building(self, building):
		'''
			Create a single building and add to the list of PSU buildings in the backing database. 
			Invalidate the cache of all buildings if there is an existing entry.  
		'''
		status = self.building_is_valid(building)

		if status['result'] == 'success':
			if model.add_building(building) == True:
				self.log.debug('create_building(): successfully added a new building')
				status = {'result': 'success', 'message': 'successfully added a new building'}
			else:
				self.log.warn('create_building(): failed to add new building to database')
				status = {'result': 'error', 'message': 'failed to add new building to database'}
		else:
			self.log.warn('create_building(): building data is not valid: ' + status['message'])
		
		return(status)

	def update_building(self, building):
		'''
			Update a single building in the list of PSU buildings from the backing database. 
			Invalidate the cache of all buildings and also the specific building cache if there is an existing entry.  
		'''
		status = self.building_is_valid(building)

		if status['result'] == 'success':
			if model.update_building(building) == True:
				self.log.debug('update_building(): successfully updated building: ' + str(building))
				status = {'result': 'success', 'message': 'successfully updated a building'}
			else:
				self.log.warn('update_building(): failed to updated building in database')
				status = {'result': 'error', 'message': 'failed to update building in database'}
		else:
			self.log.warn('create_building(): building data is not valid')
			status = {'result': 'error', 'message': 'building data is not valid'}
		
		return(status)

	def delete_building(self, building_identifier):
		'''
			Delete an existing building and adjust the cache.
		'''
		status = {'result': 'error', 'message': ''}
		if not building_identifier.isalnum():
			status = {'result': 'error', 'message': 'invalid building_identifier: identifier is not an alphanumeric'}
			self.log.debug('get_building(): ' + status['message'])
			return(status)
		
		if model.remove_building(building_identifier) == True:
			self.log.info('delete_builiding(): removed building from model: building_identifier: ' + building_identifier)
			status = {'result': 'success', 'message': 'successfully deleted a building'}
		else:
			self.log.info('delete_builiding(): failed to remove building from model: building_identifier: ' + building_identifier)
			status = {'result': 'error', 'message': 'failed to delete a building: ' + building_identifier}
		return status

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

'''
	The following functions handle routed web requests for Buildings
'''	
	
@app.route(buildings.prop.buildings_uri_path, methods = ['GET'])
def get_buildings():
	global buildings

	if request.args and 'building_identifier' in request.args:
		buildings.log.info('get_building(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
		building_identifier = request.args['building_identifier']

		status = buildings.get_building(building_identifier)
		if status['result'] <> 'success':
			abort(404, status['message'])
		else:
			return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))

	else:
		buildings.log.info('get_buildings(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
		status = buildings.get_buildings()
		if status['result'] == 'success':
			return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
		else:
			abort(400, status['message'])

@app.route(buildings.prop.buildings_uri_path + '/<building_identifier>', methods = ['GET'])
def get_building(building_identifier):
	global buildings
	
	status = buildings.get_building(building_identifier)
	if status['result'] == 'success':
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
	else:
		abort(404, status['message'])

	

@app.route(buildings.prop.buildings_uri_path, methods = ['POST'])
def create_building():
	global buildings
	if request.json:
		buildings.log.info('create_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint) + ', body: ' + str(request.json))
		building_descriptor = request.json

		status = buildings.create_building(building_descriptor)
		if status['result'] <> 'success':
			buildings.log.info('create_building() handler: failed to create building: ' + status['message'])
			abort(404, status['message'])
			
		if status['result'] == 'success':
			buildings.log.info('create_building() handler: successfully created building: ' + status['message'])
			get_result = buildings.get_building(building_descriptor['building_identifier'])
			buildings.log.info('create_building() handler: looked-up created building: ' + str(get_result))
			if get_result['result'] == 'success':
				return(make_response((get_result['message'], 200, {'Content-Type': 'application/json'})))
			else:
				abort(400, 'Building inconsistency error.')
	else:
		abort(404, 'Building descriptor not valid.')
		
@app.route(buildings.prop.buildings_uri_path + '/<building_identifier>', methods = ['DELETE'])
def delete_building(building_identifier):
	global buildings

	buildings.log.info('delete_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))

	status = buildings.delete_building(building_identifier)
	if status['result'] == 'success':
		return('building removed')
	else:
		buildings.log.info('delete_building() handler: failed to delete building: ' + status['message'])
		abort(404, status['message'])
		
@app.route(buildings.prop.buildings_uri_path, methods = ['PUT'])
def update_building():
	global buildings
	if request.json:
		buildings.log.info('update_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
		building_descriptor = request.json

		status = buildings.update_building(building_descriptor)
		if status['result'] <> 'success':
			buildings.log.info('update_building() handler: failed to update building: ' + status['message'])
			abort(404, status['message'])
			
		if status['result'] == 'success':
			buildings.log.info('update_building() handler: successfully updated building: ' + status['message'])
			get_result = buildings.get_building(building_descriptor['building_identifier'])
			buildings.log.info('update_building() handler: looked-up updated building: ' + str(get_result))
			if get_result['result'] == 'success':
				return(make_response((get_result['message'], 200, {'Content-Type': 'application/json'})))
			else:
				abort(404, 'Building inconsistency error.')
	else:
		abort(404, 'Building descriptor not valid.')
		

@app.errorhandler(400)
def custom_400(error):
	buildings.log.info('custom_400(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 400)

@app.errorhandler(404)
def custom_404(error):
	buildings.log.info('custom_404(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 404)




#app.run(host='0.0.0.0', debug = True)



		