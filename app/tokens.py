'''
Created on Sep 23, 2014

@author: dennis
'''

import logging.config
from config import config
from flask import Flask, jsonify, abort, make_response, request
#import auth
from redis import StrictRedis
import gdata.spreadsheet.service

class Tokens():
	'''
		Provide the token management service
	'''

	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('tokens')
		self.log.debug('__init__(): starting')
	
	def notify(self, log_index):
		'''
			Receive notification of a user token change event. The notify method corresponds
			to the Observer design pattern 'notify' which is called by the 'subject'
		'''
		
		status = {'result': 'error', 'message': ''}

		self.log.info("notify(): log_index: " + str(log_index))
		if log_index == '0':
			self.log.info('notify(): unit-test case data detected')
			status = {'result': 'success', 'message': "unit-test triggered"}
		else:
			# This activity should run asynchronously 
			updates = self.fetch_updates(log_index)
			self.post_updates(updates, log_index)
			# Update the local tokens from the source
			status = {'result': 'success', 'message': "index up-to-date"}
		
		return status
		
	def post_updates(self, updates, log_index):
		'''
			Update the cache with CRUD changes
		'''
		cache = StrictRedis(db=config.tokens_cache_redis_db)
		
		self.log.info('post_updates(): posting updates to local storage')
		for update in updates:			# TODO: could re-add the Redis "Pipelines" feature to combine Redis requests for better performance when available
			(user, token, date, action) = update
			if action == 'add':
				cache.hset('general', token, user)	# user-by-token -- really just existence of a token
				cache.hset('users', user, token)	# token-by-user: allow lookup of previous token on token changes
				self.log.info('post_updates(): added token for user: ' + user)
			elif action == 'delete':
				cache.hdel('general', token)	# disables the ability to authenticate
				cache.hdel('users', user)	# removes history of token
				self.log.info('post_updates(): deleted token for user: ' + user)
			elif action == 'update':
				prev_token = cache.hget('users', user)
				cache.hdel('general', prev_token)	# disables the ability to authenticate with previous token
				cache.hset('general', token, user)		# set the new token for the user
				cache.hset('users', user, token)		# set the user as possessing the new token
				self.log.info('post_updates(): updated token for user: ' + user)
			else:
				self.log.critical('post_updates(): unexpected change type: ' + action)

		if len(updates) > 0:	# don't set if there is nothing to do and also don't set if there are errors
			cache.set('log_index', log_index)
		
	def fetch_updates(self, log_update_index):
		cache = StrictRedis(db=config.tokens_cache_redis_db)
		log_prev_index = cache.get('log_index')
		
		if log_prev_index is None:
			log_prev_index = 1

		self.log.info('fetch_delta(): log_prev_index: ' + str(log_prev_index))
			
		cols = 4
		updates = []

		try:
			self.log.info('fetch_delta(): connecting to Google spreadsheet')
			client = gdata.spreadsheet.service.SpreadsheetsService()
			client.ClientLogin(config.tokens_google_client_login, config.tokens_google_client_password)
			query = gdata.spreadsheet.service.CellQuery()
			query.min_row = str(int(log_prev_index) + 1)
			query.max_row = str(log_update_index)
			cells = client.GetCellsFeed(config.tokens_spreadsheet_id, wksht_id=config.tokens_worksheet_id, query=query).entry
			self.log.info('fetch_delta(): spreadsheet list of changes')
			
			updates = []
			rows = int(log_update_index) - int(log_prev_index)
			self.log.info('fetch_delta(): fetching number of rows: ' + str(rows))
			for row in range(0,rows):
				(user, token, date, action) = [str(cell.content.text) for cell in cells[row * cols : (row + 1) * cols]]
				self.log.info('fetch_delta() updating user: ' + user + ', on date: ' + date + ', with action: ' + action)
				if not action in ('add', 'delete', 'update'):
					self.log.critical('fetch_delta() invalid action detected')
					updates = []
					break
				else:
					updates.append((user, token, date, action))
	
			self.log.info('fetch_delta(): returning update count: ' + str(len(updates)))
		except Exception as ex:
			self.log.error('fetch_delta(): exception: ' + str(ex))
			
		return updates
	
	def sync_cache(self):
		'''
			Erase the local cache of tokens and scopes, and reload from cloud storage
		'''
		
		# Collect Token management info from the cloud
		client = gdata.spreadsheet.service.SpreadsheetsService()
		client.ClientLogin(config.tokens_google_client_login, config.tokens_google_client_password)
		worksheets_feed = client.GetWorksheetsFeed(config.tokens_spreadsheet_id).entry
		worksheet_ids = {}
		for worksheet in worksheets_feed:
			worksheet_ids[worksheet.title.text] = worksheet.id.text.split('/')[-1]
			self.log.debug('sync_cache() found sheets: ' + worksheet.title.text)
		
		# Delete 'general' cache state
		cache = StrictRedis(db=config.tokens_cache_redis_db)
		cache.flushdb()	# Remove all kes from the current database
		
		# Fetch token list
		query = gdata.spreadsheet.service.CellQuery()
		query.min_row = '1'
		cells = client.GetCellsFeed(config.tokens_spreadsheet_id, wksht_id=worksheet_ids['tokens'], query=query).entry
		cols = 3
		rows = len(cells) / cols
		tokens = []
		for row in range(0, rows):
			tokens.append([str(cell.content.text) for cell in cells[row * cols : (row + 1) * cols]])
		self.log.debug('sync_cache() fetched tokens from cloud: ' + str(rows))
		
		# Fetch scopes
		scopes = {}
		
		for worksheet_title in worksheet_ids.keys():
			if worksheet_title not in ['tokens', 'change log']:	# must then be a scope list
				self.log.debug('sync_cache() fetching scope: ' + str(worksheet_title))
				scopes[worksheet_title] = []
				cells = client.GetCellsFeed(config.tokens_spreadsheet_id, wksht_id=worksheet_ids[worksheet_title], query=query).entry
				for cell in cells:
					scopes[worksheet_title].append(cell.content.text)
				self.log.debug('sync_cache() fetched scope: ' + str(worksheet_title) + ', with number of items: ' + str(len(cells)))
					
		# Build user and general cache
		for token_ent in tokens:
			(user, token, datetime) = token_ent
			cache.set(token, user)
		self.log.debug('sync_cache() added tokens, count: ' + str(len(tokens)))
		
		# Build scopes
		for (scope_name, scope_list) in scopes.items():
			for user in scope_list:
				cache.sadd(scope_name, user)
			self.log.debug('sync_cache() added scope: ' + scope_name + ', with member count: ' + str(len(scope_list)))

		# Reset the cache log index to the last entry
		num_log_entries = len(client.GetListFeed( config.tokens_spreadsheet_id, wksht_id=worksheet_ids['change log']).entry) + 1
		cache.set('log_index', num_log_entries) # Reset the cache log index to the start
		self.log.debug('sync_cache() set log_index to: ' + str(num_log_entries))
		
		
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
def notify(log_index):
	"""
		Observe token updates. Wait for call from the User Token Management Service.
		The most recent change log index is pass in. This service then fetches and applies changes starting
		from the last locally saved log index position.
	"""
	global request, token

	tokens.log.info('notify(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = tokens.notify(log_index)

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

		