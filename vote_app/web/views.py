from flask import make_response, abort, request
from . import web
from config import config
from vote_app.vote import vote
import auth
import json
		
'''
	The following functions handle routed web requests for Vote status
'''	

@web.route(config.vote_uri_path + '/<odin_name>', methods = ['GET'])
@auth.requires_auth(scope=config.people_scope_vote)
def verify_eligibility(odin_name):
	'''
		Verify eligibility to vote in the ASPSU student elections
	'''
	global request

	vote.log.info('verify_eligibility(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = vote.verify_eligibility(odin_name)
	if 'success' in status:
		return(make_response(json.dumps(status['success']), 200, {'Content-Type': 'application/json'}))
	else:
		abort(config.people_code_by_error[status['error']['type']], status)


