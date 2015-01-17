'''
Created on Sep 23, 2014

@author: dennis
'''

import logging.config
from config import config
from flask import Flask, jsonify, abort, make_response, request
#import auth
from redis import StrictRedis

class Tokens():
	'''
		Provide the token management service
	'''

	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('token')
		self.log.debug('__init__(): starting')
	
	def event_accept(self, log_index):
		'''
			Receive notification of a user token change event.
		'''
		
		status = {'result': 'error', 'message': ''}
		tokens_cache = StrictRedis(db=config.tokens_cache_redis_db)
		last_log_index = tokens_cache.get('token_index')
		self.log.info("event_accept(): last log_index: " + str(last_log_index))

		self.log.info("event_accept(): log_index: " + str(log_index))
		if log_index == '0':
			self.log.info('event_accept(): unit-test case data detected')
			status = {'result': 'success', 'message': "unit-test triggered"}
		else:
			pass
			# Update the local tokens from the source
			
		status = {'result': 'success', 'message': "index up-to-date"}
		
		return status
		
		
		
'''
if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
	#	context = daemon.DaemonContext(umask=0o002)
	#	with context:
'''

tokens = Tokens()

app = Flask(__name__)

def init_db():
	#model.init_db()
	pass

#@auth.require_auth(scope='token_manage')
@app.route(config.tokens_uri_path + '/<log_index>', methods = ['GET'])
def event_accept(log_index):
	"""
		Observe token updates. Wait for call from the User Token Management Service.
		The most recent change log index is pass in. This service then fetches and applies changes starting
		from the last locally saved log index position.
	"""
	global request, token

	tokens.log.info('token_update(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = tokens.event_accept(log_index)

	if status['result'] <> 'success':
		abort(404, status['message'])
	else:
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
		
@app.errorhandler(400)
def custom_400(error):
	token.log.info('custom_400(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 400)

@app.errorhandler(404)
def custom_404(error):
	token.log.info('custom_404(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 404)

		