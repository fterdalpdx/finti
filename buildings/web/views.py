from flask import make_response, abort, request
from . import web
from config import config
from buildings.buildings import buildings
import auth
		
'''
	The following functions handle routed web requests for Buildings
'''	
	
@web.route(config.buildings_uri_path, methods = ['GET'])
@auth.requires_auth(scope='general')
def get_buildings():
	global request

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

@web.route(config.buildings_uri_path + '/<building_identifier>/history', methods = ['GET'])
@auth.requires_auth(scope='general')
def get_building_history(building_identifier):
	global request

	buildings.log.info('get_building_history(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint) + ', with building_identifier: ' + building_identifier)

	status = buildings.get_building_history(building_identifier)
	if status['result'] <> 'success':
		abort(404, status['message'])
	else:
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))

@web.route(config.buildings_uri_path + '/<building_identifier>', methods = ['GET'])
@auth.requires_auth(scope='general')
def get_building(building_identifier):
	
	buildings.log.info('get_building(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = buildings.get_building(building_identifier)
	if status['result'] == 'success':
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
	else:
		abort(404, status['message'])

	

@web.route(config.buildings_uri_path, methods = ['POST'])
@auth.requires_auth(scope='manage_buildings')
def add_building():
	global request
	
	if request.json:
		buildings.log.info('add_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint) + ', body: ' + str(request.json))
		building_descriptor = request.json

		status = buildings.add_building(building_descriptor)
		if status['result'] <> 'success':
			buildings.log.info('add_building() handler: failed to add building: ' + status['message'])
			abort(404, status['message'])
			
		if status['result'] == 'success':
			buildings.log.info('add_building() handler: successfully added building: ' + status['message'])
			get_result = buildings.get_building(building_descriptor['building_identifier'])
			buildings.log.info('add_building() handler: looked-up added building: ' + str(get_result))
			if get_result['result'] == 'success':
				return(make_response((get_result['message'], 200, {'Content-Type': 'application/json'})))
			else:
				abort(400, 'Building inconsistency error.')
	else:
		abort(404, 'Building descriptor not valid.')
		
@web.route(config.buildings_uri_path + '/<building_identifier>', methods = ['DELETE'])
@auth.requires_auth(scope='manage_buildings')
def delete_building(building_identifier):

	buildings.log.info('delete_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))

	status = buildings.delete_building(building_identifier)
	if status['result'] == 'success':
		return('building removed')
	else:
		buildings.log.info('delete_building() handler: failed to delete building: ' + status['message'])
		abort(404, status['message'])
		
@web.route(config.buildings_uri_path, methods = ['PUT'])
@auth.requires_auth(scope='manage_buildings')
def update_building():
	global request
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
		

