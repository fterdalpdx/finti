from flask import make_response, abort, request
from . import web
from config import config
from tokens_app.tokens import tokens

#@auth.require_auth(scope='token_manage')
@web.route(config.tokens_uri_path + '/<update_id>', methods = ['GET'])
def notify(update_id):
	"""
		Observe token updates. Wait for call from the User Token Management Service.
		The most recent change log index is pass in. This service then fetches and applies changes starting
		from the last locally saved log index position.
	"""
	#global request, tokens_app

	tokens.log.info('notify(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = tokens.notify(update_id)

	if status['result'] <> 'success':
		abort(404, status['message'])
	else:
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
		
