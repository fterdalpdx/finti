'''
Created on Aug 22, 2014

@author: dennis
'''
import json
import re
from flask import request, session
from redis import StrictRedis
from oauth2lib.provider import AuthorizationProvider
from redis.client import Redis

client_id = '314'
user_id='rincewind'
client_secret = 'octarine'
finish_redirect_uri = 'http://localhost:5000/thirdparty_auth'

class Application():
	def __init__(self):
		self.redis = StrictRedis()
		
	def find(self, client_id):
		# Needs to provide:
		#	redirect_uri
		#	secret
		class C(object): pass
		
		app_json = self.redis.get(client_id)
		app = None
		if app_json is not None:
			app = C()
			app_data = json.loads(app_json)
			app.redirect_uri = app_data['redirect_uri']
			app.secret = app_data['secret']
		print('app.find(): app.redirect_uri: ' + app.redirect_uri + ', app.secret: ' + app.secret)
		return app
	
class PSUAuthorizationProvider(AuthorizationProvider):
	def __init__(self):
		self.redis = StrictRedis()

		
	def validate_client_id(self, client_id):
		"""Check that the client_id represents a valid application.

		:param client_id: Client id.
		:type client_id: str
		"""
		print('validate_client_id')
		application = Application()
		#return Application.find(client_id) is not None
		if application.find(client_id) is not None:
			print('validate_client_id: True')
		else:
			print('validate_client_id: False')
			
		return application.find(client_id) is not None

	def validate_client_secret(self, client_id, client_secret):
		"""Check that the client secret matches the application secret.

		:param client_id: Client Id.
		:type client_id: str
		:param client_secret: Client secret.
		:type client_secret: str
		"""
		print('validate_client_secret')
		#app = Application.find(client_id)
		application = Application()
		app = application.find(client_id)
		if app is not None and app.secret == client_secret:
			print('validate_client_secret: True')
			return True
		print('validate_client_secret: False')
		return False

	def validate_redirect_uri(self, client_id, redirect_uri):
		"""Validate that the redirect_uri requested is available for the app.

		:param redirect_uri: Redirect URI.
		:type redirect_uri: str
		"""
		#app = Application.find(client_id)
		application = Application()
		app = application.find(client_id)
		if app is not None:
			print('validate_redirect_uri: app is not None')
			print('validate_redirect_uri() app.redirect_uri: ' + app.redirect_uri + ', redirect_uri: ' + redirect_uri)

		# When matching against a redirect_uri, it is very important to 
		# ignore the query parameters, or else this step will fail as the 
		# parameters change with every request
		if app is not None and app.redirect_uri == redirect_uri.split('?')[0]:
			print('validate_redirect_uri: True')
			return True
		print('validate_redirect_uri: False')
		return False

	def validate_access(self):
		"""Validate that an OAuth token can be generated from the
		current session."""
		print('validate_access() session: ' + str(session) )

		try:
			if session.user_id is not None:
				print('validate_access() success')
				return True
			else:
				print('validate_access() failure')
				return False
		except Exception:
			print('validate_access() missing key')
			return True

	def validate_scope(self, client_id, scope):
		"""Validate that the scope requested is available for the app.

		:param client_id: Client id.
		:type client_id: str
		:param scope: Requested scope.
		:type scope: str
		"""
		print('validate_scope')
		return True if scope == "" else False
	
	def persist_authorization_code(self, client_id, code, scope):
		"""Store important session information (user_id) along with the
		authorization code to later allow an access token to be created.

		:param client_id: Client Id.
		:type client_id: str
		:param code: Authorization code.
		:type code: str
		:param scope: Scope.
		:type scope: str
		"""
		print('persist_authorization_code')
		key = 'oauth2.authorization_code.%s:%s' % (client_id, code)

		# Store any information about the current session that is needed
		# to later authenticate the user.
		data = {'client_id': client_id,
				'scope': scope,
				#'user_id': session.user_id }
				'user_id': user_id }

		# Authorization codes expire in 1 minute
		print('persisting_authorization_code() key: ' + key + ', value: ' + json.dumps(data))
		self.redis.setex(key, 60, json.dumps(data))

	def persist_token_information(self, client_id, scope, access_token,
								  token_type, expires_in, refresh_token,
								  data):
		"""Save OAuth access and refresh token information.

		:param client_id: Client Id.
		:type client_id: str
		:param scope: Scope.
		:type scope: str
		:param access_token: Access token.
		:type access_token: str
		:param token_type: Token type (currently only Bearer)
		:type token_type: str
		:param expires_in: Access token expiration seconds.
		:type expires_in: int
		:param refresh_token: Refresh token.
		:type refresh_token: str
		:param data: Data from authorization code grant.
		:type data: mixed
		"""

		print('persist_token_information')
		# Set access token with proper expiration
		access_key = 'oauth2.access_token:%s' % access_token
		self.redis.setex(access_key, expires_in, json.dumps(data))

		# Set refresh token with no expiration
		refresh_key = 'oauth2.refresh_token.%s:%s' % (client_id, refresh_token)
		self.redis.set(refresh_key, json.dumps(data))

		# Associate tokens to user for easy token revocation per app user
		key = 'oauth2.client_user.%s:%s' % (client_id, data.get('user_id'))
		self.redis.sadd(key, access_key, refresh_key)
	
	def from_authorization_code(self, client_id, code, scope):
		"""Get session data from authorization code.

		:param client_id: Client ID.
		:type client_id: str
		:param code: Authorization code.
		:type code: str
		:param scope: Scope to validate.
		:type scope: str
		:rtype: dict if valid else None
		"""
		print('from_authorization_code')
		key = 'oauth2.authorization_code.%s:%s' % (client_id, code)
		print('from_authorization_code() key: ' + key)
		data = self.redis.get(key)
		print('from_authorization_code() data: ' + str(data))
		if data is not None:
			print('from_authorization_code() found data')
			data = json.loads(data)

			# Validate scope and client_id
			if (scope == '' or scope == data.get('scope')) and \
				data.get('client_id') == client_id:
				print('from_authorization_code() success')
				return data

		print('from_authorization_code() fail')
		return None  # The OAuth authorization will fail at this point

	def from_refresh_token(self, client_id, refresh_token, scope):
		"""Get session data from refresh token.

		:param client_id: Client Id.
		:type client_id: str
		:param refresh_token: Refresh token.
		:type refresh_token: str
		:param scope: Scope to validate.
		:type scope: str
		:rtype: dict if valid else None
		"""
		print('from_refresh_token')
		key = 'oauth2.refresh_token.%s:%s' % (client_id, refresh_token)
		data = self.redis.get(key)
		if data is not None:
			data = json.loads(data)

			# Validate scope and client_id
			if (scope == '' or scope == data.get('scope')) and \
				data.get('client_id') == client_id:
				return data

		return None  # The OAuth token refresh will fail at this point

	def discard_authorization_code(self, client_id, code):
		"""Delete authorization code from the store.

		:param client_id: Client Id.
		:type client_id: str
		:param code: Authorization code.
		:type code: str
		"""

		key = 'oauth2.authorization_code.%s:%s' % (client_id, code)
		print('discard_authorization_code() key: ' + key)
		self.redis.delete(key)

	def discard_refresh_token(self, client_id, refresh_token):
		"""Delete refresh token from the store.

		:param client_id: Client Id.
		:type client_id: str
		:param refresh_token: Refresh token.
		:type refresh_token: str

		"""
		print('discard_refresh_token')
		key = 'oauth2.refresh_token.%s:%s' % (client_id, refresh_token)
		self.redis.delete(key)

	def discard_client_user_tokens(self, client_id, user_id):
		"""Delete access and refresh tokens from the store.

		:param client_id: Client Id.
		:type client_id: str
		:param user_id: User Id.
		:type user_id: str

		"""
		print('discard_client_user_tokens')
		keys = 'oauth2.client_user.%s:%s' % (client_id, user_id)
		pipe = self.redis.pipeline()
		for key in self.redis.smembers(keys):
			pipe.delete(key)
		pipe.execute()
		
