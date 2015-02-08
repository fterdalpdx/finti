from flask import make_response, abort, request
from . import web
from config import config
from buildings_app.buildings import buildings
import auth
		
'''
	The following functions handle routed web requests for Buildings
'''	

	
@web.route(config.buildings_uri_path, methods = ['GET'])
@auth.requires_auth(scope='general')
def get_buildings():
	'''
		Retrieve a list of all buildings
	'''
	global request

	buildings.log.info('get_buildings(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = buildings.get_buildings()
	if status['result'] == 'success':
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
	else:
		abort(config.buildings_code_by_error[status['message']], status['message'])


@web.route(config.buildings_uri_path + '/<building_identifier>/history', methods = ['GET'])
@auth.requires_auth(scope='general')
def get_building_history(building_identifier):
	'''
		Retrieve a change history list of a specific building
	'''
	global request

	buildings.log.info('get_building_history(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint) + ', with building_identifier: ' + building_identifier)

	status = buildings.get_building_history(building_identifier)
	if status['result'] <> 'success':
		abort(config.buildings_code_by_error[status['message']], status['message'])
	else:
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))


@web.route(config.buildings_uri_path + '/<building_identifier>', methods = ['GET'])
@auth.requires_auth(scope='general')
def get_building(building_identifier):
	'''
		Retrieve a specific building by the given building identifier
	'''
	buildings.log.info('get_building(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = buildings.get_building(building_identifier)
	if status['result'] == 'success':
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
	else:
		abort(config.buildings_code_by_error[status['message']], status['message'])

	

@web.route(config.buildings_uri_path, methods = ['POST'])
@auth.requires_auth(scope='manage_buildings')
def add_building():
	'''
		Creates a new Portland State University building.
	'''
	global request
	
	if request.json:
		buildings.log.info('add_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint) + ', body: ' + str(request.json))
		building_descriptor = request.json

		status = buildings.add_building(building_descriptor)
		if status['result'] <> 'success':
			buildings.log.info('add_building() handler: failed to add building: ' + status['message'])
			if status['message'] == config.buildings_err_gen:
				abort(config.buildings_code_by_error[status['message']], status['message'])
			else:
				abort(404, status['message'])
			
		if status['result'] == 'success':
			buildings.log.info('add_building() handler: successfully added building: ' + status['message'])
			get_result = buildings.get_building(building_descriptor['building_identifier'])
			buildings.log.info('add_building() handler: looked-up added building: ' + str(get_result))
			if get_result['result'] == 'success':
				return(make_response((get_result['message'], 200, {'Content-Type': 'application/json'})))
			else:
				abort(404, 'Building descriptor not valid')
	else:
		abort(404, 'Building descriptor not valid')


@web.route(config.buildings_uri_path, methods = ['PUT'])
@auth.requires_auth(scope='manage_buildings')
def update_building():
	'''
		Updates an existing Portland State University building.
	'''
	global request
	if request.json:
		buildings.log.info('update_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
		building_descriptor = request.json

		status = buildings.update_building(building_descriptor)
		if status['result'] <> 'success':
			buildings.log.info('update_building() handler: failed to update building: ' + status['message'])
			if status['message'] == config.buildings_err_gen:
				buildings.log.info('update_building() aborting with status: ' + config.buildings_code_by_error[status['message']] + ' message: ' + status['message'])
				abort(config.buildings_code_by_error[status['message']], status['message'])
			else:
				abort(404, status['message'])
			
		if status['result'] == 'success':
			buildings.log.info('update_building() handler: successfully updated building: ' + status['message'])
			get_result = buildings.get_building(building_descriptor['building_identifier'])
			buildings.log.info('update_building() handler: looked-up updated building: ' + str(get_result))
			if get_result['result'] == 'success':
				return(make_response((get_result['message'], 200, {'Content-Type': 'application/json'})))
			else:
				abort(404, 'Building descriptor not valid')
	else:
		abort(404, 'Building descriptor not valid.')

	
@web.route(config.buildings_uri_path + '/<building_identifier>', methods = ['DELETE'])
@auth.requires_auth(scope='manage_buildings')
def delete_building(building_identifier):
	'''
		Change the given building status to inactive in the list of current Portland State University buildings.
	'''
	buildings.log.info('delete_building() handler: called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))

	status = buildings.delete_building(building_identifier)
	if status['result'] == 'success':
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
	else:
		buildings.log.info('delete_building() handler: failed to delete building: ' + status['message'])
		abort(config.buildings_code_by_error[status['message']], status['message'])
		

