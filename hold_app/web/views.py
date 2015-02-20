from flask import make_response, abort, request
from . import web
from config import config
from hold_app.hold import hold
import auth
import json
		
'''
	The following functions handle routed web requests for advising hold requests
'''	

@web.route(config.hold_uri_path + '/advise/check/<student_id>', methods = ['GET'])
@auth.requires_auth(scope=config.people_scope_advise)
def get_advising_hold(student_id):
	'''
		Get the advising hold status for the given student
	'''
	
	global request

	hold.log.info('get_advising_hold(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = hold.get_advising_hold(student_id)
	if 'success' in status:
		return(make_response(json.dumps(status['success']), 200, {'Content-Type': 'application/json'}))
	else:
		abort(config.people_code_by_error[status['error']['type']], status)


@web.route(config.hold_uri_path + '/advise/auth/<advisor_id>', methods = ['GET'])
@auth.requires_auth(scope=config.people_scope_advise)
def verify_authorization(advisor_id):
	'''
		Verify that the given advisor is authorized to clear authorization holds
	'''
	
	global request

	hold.log.info('verify_authoization(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = hold.verify_authorization(advisor_id)
	if 'success' in status:
		return(make_response(json.dumps(status['success']), 200, {'Content-Type': 'application/json'}))
	else:
		abort(config.people_code_by_error[status['error']['type']], status)


@web.route(config.hold_uri_path + '/advise/clear/<advisor_id>/<student_id>', methods = ['POST'])
@auth.requires_auth(scope=config.people_scope_advise)
def clear_advising_hold(advisor_id, student_id):
	'''
		Clear the advising hold for the given student on the authorization of the given advisor
	'''
	
	global request

	hold.log.info('clear_advising_hold(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = hold.clear_advising_hold(advisor_id, student_id)
	if 'success' in status:
		return(make_response(json.dumps(status['success']), 200, {'Content-Type': 'application/json'}))
	else:
		abort(config.people_code_by_error[status['error']['type']], status)


