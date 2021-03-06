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
import daemon
from optparse import OptionParser
import socket
import requests
#from django.contrib.auth.context_processors import auth
import auth

#from flaskext.auth.permissions import self

class Tokens():
	'''
		Provide the token management service
	'''

	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('tokens')
		#self.pubsub = {}
		
	def notify(self, log_index):
		'''
			Receive notification of a user token change event. The notify method corresponds
			to the Observer design pattern 'notify' which is called by the 'subject'
		'''
		
		self.cache = StrictRedis(db=config.tokens_cache_redis_db)
		self.log.debug('notify(): connected to cache')

		status = {'result': 'error', 'message': ''}

		self.log.info("notify(): log_index: " + str(log_index))
		try:
			self.log.info('notify(): published notify item to pubsub queue')
			self.cache.publish(config.tokens_pubsub_channel, log_index)
			status = {'result': 'success', 'message': "token indexing system notified"}
		except Exception as ex:
			status = {'result': 'error', 'message': "queue is not responding"}
		
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
				cache.hset('general', token, user)	# future method - user-by-token -- really just existence of a token
				cache.hset('users', user, token)	# future-method - token-by-user: allow lookup of previous token on token changes
				cache.set(token, user)	# Current method
				self.log.info('post_updates(): added token for user: ' + user)
			elif action == 'delete':
				cache.hdel('general', token)	# future method - disables the ability to authenticate
				cache.hdel('users', user)	# future method - removes history of token
				cache.delete(token)
				self.log.info('post_updates(): deleted token for user: ' + user)
			elif action == 'update':
				prev_token = cache.hget('users', user)
				cache.hdel('general', prev_token)	# future method - disables the ability to authenticate with previous token
				cache.hset('general', token, user)		# future method - set the new token for the user
				cache.hset('users', user, token)		# future method - set the user as possessing the new token
				cache.set(token, user)
				self.log.info('post_updates(): updated token for user: ' + user)
			else:
				self.log.critical('post_updates(): unexpected change type: ' + action)

		if len(updates) > 0:	# don't set if there is nothing to do and also don't set if there are errors
			cache.set('log_index', log_index)
		
	def fetch_updates(self, log_update_index):
		cache = StrictRedis(db=config.tokens_cache_redis_db)
		log_prev_index = cache.get('log_index')
		
		if int(log_update_index) <= int(log_prev_index):
			log_prev_index = '0'
		
		
		self.log.info('fetch_updates(): log_prev_index: ' + str(log_prev_index) + ', log_update_index: ' + str(log_update_index))
			
		cols = 4
		updates = []

		try:
			self.log.info('fetch_updates(): connecting to Google spreadsheet')
			client = gdata.spreadsheet.service.SpreadsheetsService()
			client.ClientLogin(config.tokens_google_client_login, config.tokens_google_client_password)
			query = gdata.spreadsheet.service.CellQuery()
			query.min_row = str(int(log_prev_index) + 1)
			query.max_row = str(log_update_index)
			cells = client.GetCellsFeed(config.tokens_spreadsheet_id, wksht_id=config.tokens_worksheet_id, query=query).entry
			self.log.info('fetch_updates(): spreadsheet list of changes')
			
			updates = []
			rows = int(log_update_index) - int(log_prev_index)
			self.log.info('fetch_updates(): fetching number of rows: ' + str(rows))
			for row in range(0,rows):
				(user, token, date, action) = [str(cell.content.text) for cell in cells[row * cols : (row + 1) * cols]]
				self.log.info('fetch_updates() updating user: ' + user + ', on date: ' + date + ', with action: ' + action)
				if not action in ('add', 'delete', 'update'):
					self.log.critical('fetch_updates() invalid action detected')
					updates = []
					break
				else:
					updates.append((user, token, date, action))
	
			self.log.info('fetch_updates(): returning update count: ' + str(len(updates)))
		except Exception as ex:
			self.log.error('fetch_updates(): exception: ' + str(ex))
			
		return updates
	
	def sync_cache(self):
		'''
			Update the local token and scope cache from cloud storage
		'''
		
		# Collect Token management info from the cloud
		client = gdata.spreadsheet.service.SpreadsheetsService()
		client.ClientLogin(config.tokens_google_client_login, config.tokens_google_client_password)
		worksheets_feed = client.GetWorksheetsFeed(config.tokens_spreadsheet_id).entry
		worksheet_ids = {}
		for worksheet in worksheets_feed:
			worksheet_ids[worksheet.title.text] = worksheet.id.text.split('/')[-1]
			self.log.debug('sync_cache() found sheets: ' + worksheet.title.text)
		
		# Connect to the local token cache
		cache = StrictRedis(db=config.tokens_cache_redis_db)
		
		# Fetch token list
		query = gdata.spreadsheet.service.CellQuery()
		query.min_row = '1'
		cells = client.GetCellsFeed(config.tokens_spreadsheet_id, wksht_id=worksheet_ids['tokens'], query=query).entry
		cols = 3
		rows = len(cells) / cols
		cloud_tokens = []
		token_ent_by_token = {}
		for row in range(0, rows):
			token_ent = [str(cell.content.text) for cell in cells[row * cols : (row + 1) * cols]]
			(user, token, datetime) = token_ent
			token_ent_by_token[token] = token_ent
			cloud_tokens.append(token_ent)
		self.log.debug('sync_cache() fetched tokens from cloud: ' + str(rows))
		
		# Add our admin token for maintaining caches
		admin_token_hash = auth.calc_hash(config.admin_token)
		admin_ent = ('finti_admin@pdx.edu', admin_token_hash,'')
		token_ent_by_token[admin_token_hash] = admin_ent
		cloud_tokens.append(admin_ent)

		# Fetch scopes
		cloud_scopes = {}
		
		for worksheet_title in worksheet_ids.keys():
			if worksheet_title not in ['tokens', 'change log']:	# must then be a scope list
				self.log.debug('sync_cache() fetching scope: ' + str(worksheet_title))
				cloud_scopes[worksheet_title] = []
				cells = client.GetCellsFeed(config.tokens_spreadsheet_id, wksht_id=worksheet_ids[worksheet_title], query=query).entry
				for cell in cells:
					cloud_scopes[worksheet_title].append(cell.content.text)
				self.log.debug('sync_cache() fetched scope: ' + str(worksheet_title) + ', with number of items: ' + str(len(cells)))
		
		# At this point the current live state of all tokens and scopes has been retrieved from cloud storage			

		#cache.flushdb()	# Remove all keys from the current database -- ok in dev, evil in practice

		# Eliminate keys in local cache which are not in the cloud cache
		for token in cache.keys():
			if cache.type(token) <> 'string':	# This is a scope set, and not a token
				continue
			if len(token) < 60 or len(token) > 70:		# The cache item is the wrong size to be a token
				continue
			if token not in token_ent_by_token:
				self.log.info('sync_cache() eliminating stale token: ' + token)
				cache.delete(token)
		# Update keys in the local cache
		
		# Build user and general cache
		for token_ent in cloud_tokens:
			(user, token, datetime) = token_ent
			self.log.debug('sync_cache() adding to local cache, token: ' + token[0:5] + ', user: ' + str(user))
			cache.set(token, user)
		self.log.debug('sync_cache() updated tokens, count: ' + str(len(cloud_tokens)))
		
		# Eliminate keys in local cache which are not in the cloud cache
		for (cloud_scope_name, cloud_scope_list) in cloud_scopes.items():
			for user in cache.smembers(cloud_scope_name):
				if user not in cloud_scope_list:
					cache.srem(cloud_scope_name, user)
					self.log.info('sync_cache() eliminated user: ' + user + ' from scope: ' + cloud_scope_name)

		# TODO: Eliminate deactivated scopes
		
		# Build scopes
		for (scope_name, scope_list) in cloud_scopes.items():
			for user in scope_list:
				cache.sadd(scope_name, user)
			self.log.debug('sync_cache() added scope: ' + scope_name + ', with member count: ' + str(len(scope_list)))

		# Reset the cache log index to the last entry
		num_log_entries = len(client.GetListFeed( config.tokens_spreadsheet_id, wksht_id=worksheet_ids['change log']).entry) + 1
		cache.set('log_index', num_log_entries) # Reset the cache log index to the start
		self.log.debug('sync_cache() set log_index to: ' + str(num_log_entries))
		
		
	def listen(self):
		'''
			Listen on a pub/sub channel for token cache update requests
		'''
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('tokens')
		
		cache = StrictRedis(db=config.tokens_cache_redis_db)
		self.log.debug('listen(): connected to cache')

		self.log.info('listen(): starting listener')
		pubsub = cache.pubsub()
		pubsub.subscribe([config.tokens_pubsub_channel])
		self.log.info('listen(): subscribed to channel: ' + config.tokens_pubsub_channel)

		myhostname = socket.gethostname()
		neighbors = [host for host in config.neighbors if host <> myhostname]
		self.log.info('listen(): neighbors are: ' + str(neighbors))
		
		for item in pubsub.listen():
			self.log.info('listen(): item detected: ' + str(item))
			value = str(item['data'])
			message_type = str(item['type'])
			if message_type <> 'message':
				continue
			is_echo = False
			if value.startswith('echo'):
				is_echo = True
				value = value.split()[1]
				self.log.info('listen(): token echo change detected: ' + value)
				
			if value.isdigit():
				# This must be a token change
				self.log.info('listen(): token change item seen: ' + str(item['data']))
				if value == '0':
					self.log.info('notify(): unit-test case data detected')
				else:
					updates = self.fetch_updates(value)
					self.post_updates(updates, str(value))
					if is_echo == False:
						self.log.info('listen(): alerting neighbors of change')
						for neighbor in neighbors:
							try:
								requests.get('http://' + neighbor + ':8888/inf/v1/tokens/echo ' + value)
								self.log.info('listen(): alerted neighbor of change: ' + neighbor)
							except Exception:
								self.log.warn('listen() failed to contact neighbor: ' + neighbor)
							
				self.log.info('listen(): finished processing token change for item: ' + str(item['data']))
			else:
				# This must be a scope change
				self.log.info('listen(): scope change item seen: ' + str(item['data']))
				self.sync_cache()
				
if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	parser.add_option("-f", "--fore", dest="fore", action='store_true', default=False, help="Run as a foreground process instead of a daemon")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
		if options.fore:
			tokens = Tokens()
			print '\033]0;Tokens\a' 
			tokens.listen()
		else:
			with daemon.DaemonContext():
				daemon_tokens = Tokens()
				daemon_tokens.listen()



		