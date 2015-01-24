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

		# Check Redis. Fail right-away if Redis is down - verifies infrastructure
		
		# Do a web request for a single building - verifies data quality
		
		# Check db -- if down set flag to not expire data. Do not fail if db is down
		
		# Check if down for maintenance 

		status = {'result': 'success', 'message': "success"}
		
		return status
		
health = Health()

		
		