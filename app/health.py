'''
Created on Sep 23, 2014

@author: dennis
'''

import logging.config
from config import config
from flask import Flask, jsonify, abort, make_response, request

class Health():
	'''
		Provide Health Check service
	'''

	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('health')
		self.log.debug('__init__(): starting')
	
	def check_health_status(self):
		'''
			Verify that all necessary systems are available and running correctly.
		'''
		
		status = {'result': 'error', 'message': 'failure'}

		self.log.info("check_health_status(): starting health check")
		
		# The per component health checks go here
		
		status = {'result': 'success', 'message': "success"}
		
		return status
		
health = Health()

app = Flask(__name__)

def init_db():
	#model.init_db()
	pass

@app.route(config.health_uri_path, methods = ['GET'])
def health_check_status():
	"""
		route and handle health check request
	"""
	global request, health

	health.log.info('health_check_status(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = health.check_health_status()

	if status['result'] <> 'success':
		abort(404, status['message'])
	else:
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
		
@app.errorhandler(400)
def custom_400(error):
	health.log.info('custom_400(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 400)

@app.errorhandler(404)
def custom_404(error):
	health.log.info('custom_404(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 404)

		