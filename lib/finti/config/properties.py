'''
Created on Sep 23, 2014

@author: dennis
'''
from Crypto.Cipher import AES
#from Crypto import Random
import os, sys
import binascii
import json
import os
from Crypto.SelfTest import SelfTestError

class Properties(object):
	def __init__(self, key_file = 'finti.key'):
		self.BLOCK_SIZE = 16
		self.PADDING = '{'
		#PROD_HOSTS = ['sagami', 'itabashi', 'ortus', 'kanagawa', 'hakone', 'shibuya', 'tokaido', 'yamate']
		#STAGE_HOSTS = ['cyril', 'pam']

		# First setup the cipher for common global properties, then later set the key for subclassed properties	
		secret = ''
		for path in sys.path:
			keyTgt = path + '/' + 'finti.key'
			if os.path.isfile(keyTgt):
				with open(keyTgt, 'r') as key:
					secret = key.read().strip()
				break
		
		if not secret == '':
			self.cipher = AES.new(binascii.a2b_hex(secret)) 

		if 'RELEASE' in os.environ:
			release = os.environ['RELEASE']
			if release in ['DEV', 'STAGE', 'PROD']:
				self.release = release
			else:
				self.release = 'DEV'
		else:
			self.release = 'DEV'
			
		# Setup common project paths to allow relative pathing for config properties	
		self.base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../..')
		self.db_path = os.path.join(os.path.dirname(self.base_path), '../../db')
		self.etc_path = os.path.join(os.path.dirname(self.base_path), 'etc')
		self.log_path = os.path.join(os.path.dirname(self.base_path), '../../var/log')

		# Properties below
		self.logging_conf_dict = json.load(open(os.path.join(self.etc_path, 'logging.json'),'r'))
		for handler in self.logging_conf_dict['handlers'].values():
			if 'filename' in handler:
				handler['filename'] = handler['filename'].replace('BASE', self.log_path)

		self.lms_password = self.decode('e370c14f0909ae58e60f67784ee7138a')
		self.lms_login = 'bbce6'

		if self.release == 'DEV':
			self.database_host = 'devl.banner.pdx.edu'
			self.database_instance = 'DEVL'
		if self.release == 'STAGE':
			self.database_instance = 'TEST'
			self.database_host = 'devl.banner.pdx.edu'
		if self.release == 'PROD':
			self.database_host = 'oprd.banner.pdx.edu'
			self.database_instance = 'OPRD'

		self.database_port = '1526'

		self.database_dsn = (self.database_host, self.database_port, self.database_instance)
			
							
		self.buildings_api_version = '1.0'
		self.buildings_uri_path = '/erp/gen/%s/buildings' % self.buildings_api_version
		self.buildings_cache_enabled = False
		self.buildings_cache_redis_db = 10
		self.buildings_cache_ttl = 3600		# Cache time-to-live in seconds
		self.required_fields = {
			'long_name': 	{'max_len': 60, 'min_len': 1, 'type': unicode, 'case': 'mixed' },
			'short_name':	{'max_len': 30, 'min_len': 1, 'type': unicode, 'case': 'mixed' },
			'building_code': {'max_len': 6, 'min_len': 1, 'type': unicode, 'case': 'upper'},
			'building_identifier': {'max_len': 10, 'min_len': 1, 'type': unicode, 'case': 'upper'},
			'street_address': {'max_len': 75, 'min_len': 1, 'type': unicode, 'case': 'upper'},
			'city': {'max_len': 50, 'min_len': 1, 'type': unicode, 'case': 'upper'},
			'state_code': {'max_len': 2, 'min_len': 2, 'type': unicode, 'case': 'upper'},
			'zipcode': {'max_len': 11, 'min_len': 5, 'type': unicode, 'case': 'upper'},
			'centroid_lat': {'type': float},
			'centroid_long': {'type': float},
			'rlis_lat': {'type': float},
			'rlis_long': {'type': float},
			'geolocate_lat': {'type': float},
			'geolocate_long': {'type': float}
		}

		# Properties above		

		# Reset the cipher for subclassed Properties
		
		secret = ''
		for path in sys.path:
			keyTgt = path + '/' + key_file
			if os.path.isfile(keyTgt):
				with open(keyTgt, 'r') as key:
					secret = key.read().strip()
				break
		
		if not secret == '':
			self.cipher = AES.new(binascii.a2b_hex(secret)) 

	def _gen_secret(self):
		return os.urandom(self.BLOCK_SIZE)
		
	def encode(self, text):
		pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING		
		return binascii.hexlify(self.cipher.encrypt(pad(text))).decode('utf-8')

	def decode(self, enciphered_text):
		return self.cipher.decrypt(binascii.a2b_hex(enciphered_text)).decode('utf-8').rstrip(self.PADDING)

	def get(self, key):
		if self.release_level == 'test':
			if (key + '_test') in self.__dict__:
				key = key + '_test'
		return self.__dict__[key]

