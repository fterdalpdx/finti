'''
Created on Sep 23, 2014

@author: dennis
'''

import logging.config
from config import config
from flask import Flask, jsonify, abort, make_response, request
from redis import StrictRedis
from werkzeug.test import Client
from werkzeug.datastructures import Headers
import auth
import base64
import json

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
		
		try:
			cache = StrictRedis(db=config.health_cache_redis_db)
			cache.set('test', 'test')
			rv = cache.get('test')
			if rv <> 'test':
				return {'result': 'error', 'message': 'redis is not responding correctly'}
		except Exception as ex:
			self.log.critical("check_health_status() redis is not responding: " + str(ex))
			return {'result': 'error', 'message': 'redis is not responding'}
			
		# Check if down for maintenance
		
		cache = StrictRedis(db=config.health_cache_redis_db)
		is_maintenance = cache.get('is_maintenance')
		if is_maintenance == 'true':
			return {'result': 'error', 'message': 'system is down for maintenance'}

		# Do a web request for a single building - verifies data quality
		
		try:
			cache = StrictRedis(db=config.tokens_cache_redis_db)
			token = config.test_token
			token_hash = auth.calc_hash(token)
			cache.set(token_hash, 'test@test')
			h = Headers()
			h.add('Authorization',
				  'Basic ' + base64.b64encode(token + ':'))
			rv = Client.open(self.client, path='/erp/gen/1.0/buildings',
							 headers=h)
			buildings_json = rv.data
			buildings = json.loads(buildings_json)
			
			if len(buildings) < 60:
				self.log.critical("check_health_status(): building data failure")
				return {'result': 'error', 'message': 'building data failure'}
			cache.delete(token_hash)
		except Exception as ex:
			self.log.critical("check_health_status(): building data failure")
			return {'result': 'error', 'message': 'building data failure'}
		
		# Check db -- if down set flag to not expire data. Do not fail if db is down
		

		status = {'result': 'success', 'message': "success"}
		
		return status
		
health = Health()

		
		