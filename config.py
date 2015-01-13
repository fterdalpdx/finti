'''
Created on Sep 23, 2014

@author: dennis
'''
from Crypto.Cipher import AES
import os, sys
import binascii
import json

class Config(object):
	# An enumeration of release levels:
	development = 	'development'
	testing =		'testing'
	production = 	'production'
	
	def __init__(self, key_file = 'finti.key'):
		self.BLOCK_SIZE = 16
		self.PADDING = '{'

		# First setup the cipher for common global properties, then later set the key for sub-classed properties	
		secret = ''
		for path in sys.path:
			keyTgt = path + '/' + 'finti.key'
			if os.path.isfile(keyTgt):
				with open(keyTgt, 'r') as key:
					secret = key.read().strip()
				break
		
		if not secret == '':
			self.cipher = AES.new(binascii.a2b_hex(secret)) 

		# Setup common project paths to allow relative pathing for config properties	
		self.base_path = os.path.abspath(os.path.dirname(__file__))
		self.db_path = os.path.join(self.base_path, 'db')
		self.etc_path = os.path.join(self.base_path, 'etc')
		self.log_path = os.path.join(self.base_path, 'var/log')

		# Properties below
		
		self.logging_conf_dict = json.load(open(os.path.join(self.etc_path, 'logging.json'),'r'))
		for handler in self.logging_conf_dict['handlers'].values():
			if 'filename' in handler:
				handler['filename'] = handler['filename'].replace('BASE', self.log_path)


		# D A T A B A S E
		
		self.lms_password = self.decode('e370c14f0909ae58e60f67784ee7138a')
		self.lms_login = 'bbce6'
		self.database_port = '1526'


		# B U I L D I N G S

		self.buildings_api_version = '1.0'
		self.buildings_uri_path = '/erp/gen/%s/buildings' % self.buildings_api_version
		self.buildings_cache_enabled = False
		self.buildings_cache_redis_db = 10
		self.buildings_cache_ttl = 3600		# Cache time-to-live in seconds

		# L D A P
		
		self.ldap_dn = 'uid=finti,ou=service,dc=pdx,dc=edu'
		self.ldap_password = self.decode('811ab624272946c5b0eef331279985a01952861af321f5d9820ea452fe24a8a8')
		
		# A C T I V E   D I R E C T O R Y
		
		
		# V A L I D A T I O N
		
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
			'geolocate_long': {'type': float},
			'from_date': {'max_len': 10, 'min_len': 10, 'type': unicode, 'case': 'upper'},
			'to_date': {'max_len': 10, 'min_len': 10, 'type': unicode, 'case': 'upper'},
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

	def init_app(self, app):
		pass

	def _gen_secret(self):
		return os.urandom(self.BLOCK_SIZE)
		
	def encode(self, text):
		pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING		
		return binascii.hexlify(self.cipher.encrypt(pad(text))).decode('utf-8')

	def decode(self, enciphered_text):
		return self.cipher.decrypt(binascii.a2b_hex(enciphered_text)).decode('utf-8').rstrip(self.PADDING)


class DevelopmentConfig(Config):
	database_host = 'devl.banner.pdx.edu'
	database_instance = 'DEVL'
	ldap_url = 'ldaps://kaylee.oit.pdx.edu:636/'
	
	def __init__(self):
		super(DevelopmentConfig, self).__init__()
		self.database_dsn = (self.database_host, self.database_port, self.database_instance)
		
class TestingConfig(Config):
	database_host = 'devl.banner.pdx.edu'
	database_instance = 'TEST'
	ldap_url = 'ldaps://inara.oit.pdx.edu:636/'
	
	def __init__(self):
		super(TestingConfig, self).__init__()
		self.database_dsn = (self.database_host, self.database_port, self.database_instance)

class ProductionConfig(Config):
	database_host = 'oprd.banner.pdx.edu'
	database_instance = 'OPRD'
	ldap_url = 'ldaps://ldap-bulk.oit.pdx.edu:636/'
	
	def __init__(self):
		super(ProductionConfig, self).__init__()
		self.database_dsn = (self.database_host, self.database_port, self.database_instance)


release_level = os.environ['RELEASE_LEVEL']

if release_level == Config.development:
	config = DevelopmentConfig()
elif release_level == Config.testing:
	config =TestingConfig()
elif release_level == Config.production:
	config = ProductionConfig()
else:
	config = DevelopmentConfig()

config.release_level = release_level

