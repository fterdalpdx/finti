'''
Created on Jan 15, 2015

@author: dennis
'''
from flask import Response, request, make_response
from functools import wraps
from redis import StrictRedis
import hashlib
import binascii
from config import config

def check_auth(login, password, required_scope):
	"""This function is called to check if a login, password, and scope combination is valid. """

	# Hash the login, the password is ignored
	login_hash = calc_hash(login)
	cache = StrictRedis(db=config.tokens_cache_redis_db)	# TODO: Should be at application scope instead of request scope
	user = cache.get(login_hash)	# lookup our person
	#print('check_auth: login: ' + login + ' scope: '+ required_scope + ', user: ' + str(user))
	if (user is None):				# if the user has a valid token
		return False
	elif (required_scope == 'general'):
		return True
	elif (cache.sismember(required_scope, user) == True): 
		return True				# and the user has the required scope
	else:
		return False			# but the user does not have the required scope

def calc_hash(token):
	hash_raw = hashlib.sha256(token)
	return(binascii.hexlify(hash_raw.digest()))
			
def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to provide proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})

def forbidden():
	"""Informs of lack of authorization"""
	return make_response('Forbidden', 403, {'Content-Type': 'application/json'})

def requires_auth(scope=""):
	def requires_auth_wrapper(f):
		@wraps(f)
		def decorated(*args, **kwargs):
			auth = request.authorization
			if not auth:
				return authenticate()
			if not check_auth(auth.username, auth.password, scope):
				return forbidden()
			return f(*args, **kwargs)
		return decorated
	return requires_auth_wrapper
