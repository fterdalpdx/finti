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

		# T O K E N S
		
		self.tokens_api_version = '1.0'
		self.tokens_uri_path = '/erp/gen/%s/tokens' % self.tokens_api_version
		self.tokens_cache_redis_db = 7
		self.tokens_google_api_key = self.decode('d2f4b41a46a42bf97cddd1917361c37e01a326edb35a26daf344be586ab6d90fbe964da64f69f7aa4a745024857832ac')
		self.tokens_google_oauth_key = self.decode('ebf2e6dd8f52e75726c72db25a0d0483422fd2e00358f7988a7d444f46cd6542ec71b816abbe9d7d61983e7bc8968704f552e55610def39cd1ebe0a847876ea8dda1a1075668c3851b242830178b08e6aa2f4dce260089544f476ae7faa51a6d5d2813386fade0d38d97c24a1369c4c6b61ee18550c05662ccf05a30b800fcead5ef65d59e2e1a2ac7077cb89f7356214c83a6bfa359c469df19c584f020d90ca997857269cfd166336901bd261e4044dfb8220f1fb2428c9e64984ddbdb9f0afd42d53948730b3fedcdbbbf925fc48df92c2435c2d14b669675a9091214e4622f80b66654299c2c4f8c932cea5111448e851b2b61ddbe4bf12de23db7e201322c8c5beea43ea7d17263ba9105a7494239072bd3311399bb4aec1bf9ee4f056fcc6a7d1f4c62231808ccaea77efa5217b39e3be3732457e4790e0a9134ff28f09760f016b835aa11cb45d23f3920e1d857f9ae80b22d0bdee1acba1e1ae3af0763013c589e072b6dbe7ed51551022826acc353b13b4d4f678602268487cdc86fc5573d62ad4f66208dd32cb3e3f672b15466eae9e3673a1a8ee8fc09fe6ba82c50fe1d9dffc5add9829515996ade43b7c36a25c6b20f4115aa0ac3ccca1a866cb5640104c1f3b766af63f8454f7e23e062d0f2c08a67ef37012da1b9f7bddbaf56c501011fa70515957a44763f17a8300ac8c1e55d06c2ca9564edb20a8156dc3781f56f6d48b787ad903e462e4ded5e92e853934c4d43b92f858ac709844fc13480e265cae45f42dd589a543ef4457934ab543bc1f7288b6df3a19a5e820f7aa5654bb4d16d35babb83e6d091b4ba10c973d7bbcd98b0803f3594f24868a44cd6f21f6e6b16b7f8a7158a236019dfc44ee4ea5b040cf39e7d74594ab90bfc3c9ee04548237e10878d3e0c017571a7738c1c5c627c752a9a109be45ee858fa98da681062fb89246ac331319484f930ea78dbad4be91a3870a9637a91a4cca289855058aa8e0313ac006ba7a6d35b06b0a8260bd141e0797eb209960117a9bcebe7a072151087fbd229f83af14ac549461a44dca5e2929286e312fd16dba70171d8f0474946f13012906a84549111347b2af8711b37d42d98fafc32f256d15cebf3b20cf6b639af54774f43c51ba988edefdd2c45de6849e6d77f959ed6c08104cc4c6909202cd70feb730f3062d5df570aa6ef799e6a67f1699ce8864981f65ae24ec943ca73dfeb9d650d51ef02ee0e473a72545bf3591d08ae58519f693a365da4800c763cfb762e46674cd0d47de297b111908b1bed2486a0c304f6402ca0757d3f885d172ab8bc360758d4ef170f2eda1ce8b2b1817812daf82e4f592a1e92f4f59a054472c658242c59601406ca31b9b106e4683bb27073f44bfecb5f8a30ff72f709419268c159af058dc94190c7a236371f56ff8e796849e4ca63544e324c5e26d9b1c2a665092d31421859ee025d822074a63de380b25c840c444d7465370a97f76211035571a3929d1e738d1031e88e6417606edc8fddbf64194ce1de7dc1b4d52b6d771808e6dd17159467adb7fb9d40f8173408973ed522ef348f1cca6d9f86d1cf00c2d1d5ca0fb3479892ec63b93334a662bf339e4cece17a747a083ad80c5a2cc308c05400476e60c83b3f1839f1ed458796ec25ac6a557e8c93aa092b77d4f54d1acb767be78c5650c53dae2decd4e0a7dd244264624eb9e9d1600ada95b2c745dc96402c2d76b16b3cf7ff83acc911188223892038c31e67')
		self.tokens_google_client_login = "googlesites@pdx.edu"
		self.tokens_google_client_password = self.decode('3cd633974083723b3d81f81b9f74cf3f')
		self.tokens_pubsub_channel = 'tokens'
		
		# L D A P
		
		self.ldap_dn = 'uid=finti,ou=service,dc=pdx,dc=edu'
		self.ldap_password = self.decode('811ab624272946c5b0eef331279985a01952861af321f5d9820ea452fe24a8a8')

		# M I S C
		
		self.docs_url = 'https://sites.google.com/a/pdx.edu/web-services/'
		self.pushbullet_api_token = self.decode('cc17ba4b11a68924fb4ca1dd0f192861469f767067427456b12973f9acf3840422bd016e8820b8556afdc97295dc49c5')
		
		# A C T I V E   D I R E C T O R Y
		
		# H E A L T H   C H E C K
		
		self.health_uri_path = '/status'
		self.health_cache_redis_db = 5
		
		# T E S T I N G
		
		self.test_token = self.decode('4d5142f10a8903f7e1eb36690133a9970c55497726426d72e7d8b26d8d4c6cdc7cc5c2d9194b9a1aca5c547ee9fbe3bd')
		
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
	tokens_spreadsheet_id = '1x7XfLNokm1YVkKbGrBQA4Ql3C5ifjVyGTVd1hbEKjlw'
	tokens_worksheet_id = 'od6'
	#tokens_pub_to = ['tama.oit.pdx.edu']
	tokens_pub_to = ['localhost']
	redis_hosts = tokens_pub_to
	tokens_account_url = 'https://script.google.com/a/macros/pdx.edu/s/AKfycbzTj8aFkCAJSrx997q3nHw_dAxZBXAZy2g2n40I4aqLcARfMA8/exec'
	doc_url = ''
	
	def __init__(self):
		super(DevelopmentConfig, self).__init__()
		self.database_dsn = (self.database_host, self.database_port, self.database_instance)
		
class TestingConfig(Config):
	database_host = 'test.banner.pdx.edu'
	database_instance = 'TEST'
	ldap_url = 'ldaps://inara.oit.pdx.edu:636/'
	tokens_spreadsheet_id = '1hPN8DRqB5l-S0R1dWcP14P4TzSwACCalt5MZryDOhTY'
	tokens_worksheet_id = 'ozcjjmt'
	tokens_pub_to = ['kiso.oit.pdx.edu', 'yoshino.oit.pdx.edu']
	redis_hosts = tokens_pub_to
	tokens_account_url = 'https://script.google.com/a/macros/pdx.edu/s/AKfycbyu8hIMQgUldW51xvKOzhUYyCkCNeuUCGTJmS1gsBIBVEK3hJU/exec'
	doc_url = ''
	
	def __init__(self):
		super(TestingConfig, self).__init__()
		self.database_dsn = (self.database_host, self.database_port, self.database_instance)

class ProductionConfig(Config):
	database_host = 'oprd.banner.pdx.edu'
	database_instance = 'OPRD'
	ldap_url = 'ldaps://ldap-bulk.oit.pdx.edu:636/'
	tokens_spreadsheet_id = '1aMQkO1QDrNQUhOrbHVso6SA9Y4q83utfMQtGIuj2Cn8'
	tokens_worksheet_id = 'ovq5ph6'
	tokens_pub_to = ['agano.oit.pdx.edu', 'shinano.oit.pdx.edu']
	redis_hosts = tokens_pub_to
	tokens_account_url = 'https://script.google.com/a/macros/pdx.edu/s/AKfycbyxw8T7ruDqESWppCDtyhn20xnDESGxffF_MC5V5y37PCoyGaU/exec'
	doc_url = ''
	
	def __init__(self):
		super(ProductionConfig, self).__init__()
		self.database_dsn = (self.database_host, self.database_port, self.database_instance)


release_level = os.environ['RELEASE_LEVEL']

if release_level == Config.development:
	config = DevelopmentConfig()
elif release_level == Config.testing:
	config = TestingConfig()
elif release_level == Config.production:
	config = ProductionConfig()
else:
	config = DevelopmentConfig()

config.release_level = release_level

