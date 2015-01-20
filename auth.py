'''
Created on Jan 15, 2015

@author: dennis
'''
from flask import Response, request
from functools import wraps
from redis import StrictRedis
import hashlib
import base64
from config import config

def check_auth(login, password, required_scope):
	"""This function is called to check if a login /
	password combination is valid.
	"""
	
	# Hash the login, the password is ignored
	hash_raw = hashlib.sha256(login)
	login_hash = base64.encodestring( hash_raw.digest()).strip()
	
	cache = StrictRedis(db=config.tokens_cache_redis_db)	# TODO: Should be at application scope instead of request scope
	user = cache.get(required_scope + login_hash)	# lookup our person
	
	return not (user is None)

def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})
	
def requires_auth(scope=""):
	def required_auth_wrapper(f):
		@wraps(f)
		def decorated(*args, **kwargs):
			auth = request.authorization
			if not auth or not check_auth(auth.username, auth.password, scope):
				return authenticate()
			return f(*args, **kwargs)
		return decorated
	return required_auth_wrapper
