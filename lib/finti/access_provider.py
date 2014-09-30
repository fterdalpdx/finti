'''
Created on Aug 27, 2014

@author: dennis
'''

import json
import re 
from flask import request, session
from flask import app, Flask
from oauth2lib.provider import ResourceProvider, ResourceAuthorization 
from datetime import datetime
from redis import StrictRedis

app = Flask(__name__)

class PSUResourceAuthorization(ResourceAuthorization):
	"""Subclass ResourceAuthorization to add user_id attribute.""" 
	user_id = None  
	# Add any other parameters you would like to associate with 
	# this authorization (OAuth session) 

class PSUResourceProvider(ResourceProvider): 
	_redis = None 
	
	@property 
	def redis(self): 
		if not self._redis: 
			self._redis = StrictRedis()
		return self._redis 
	
	@property
	def authorization_class(self): 
		print('authorization_class()')
		return PSUResourceAuthorization 
	
	def get_authorization_header(self): 
		"""Return the request Authorization header. 
		
		:rtype: str """
		print('get_authorization_header()')
		return request.headers.get('Authorization') 
	
	def validate_access_token(self, access_token, authorization):
		"""Validate the received OAuth token in our unexpired tokens. 
			:param access_token: Access token. 
			:type access_token: str 
			:param authorization: Authorization object. 
			:type authorization: PSUResourceAuthorization """ 

		key = 'oauth2.access_token:%s' % access_token
		data = self.redis.get(key) 
		print('validate_access_token() key: ' + key + ', data: ' + str(data))
		if data is not None: 
			data = json.loads(data)
			ttl = self.redis.ttl(key) 
			# Set any custom data on the Authorization here
			authorization.is_valid = True
			authorization.client_id = data.get('client_id')
			authorization.user_id = data.get('user_id') 
			authorization.expires_in = ttl 

resource_provider = PSUResourceProvider()

#from my_company_oauth import resource_provider

class Session: 
	def __init__(self):
		# Handle OAuth Authorization and store on the session object
		self.authorization = resource_provider.get_authorization()


@app.route("/protected/resource")
def some_resource():

	session = Session()
	# Ensure that this request is made with a valid OAuth
	# access token.
	if not session.authorization.is_oauth:
		raise Exception("Not authorized")
	
	print('some_resource(): is_valid: ' + str(session.authorization.is_valid))
	# Since we subclassed the Authorization class
	# we have access to all of it's properties
	#user = User.find(session.authorization.user_id)

	# Return the secret answer
	return "The code is 42"

if __name__ == '__main__':
	app.run(debug=True, port=5002)