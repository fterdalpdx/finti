from flask.ext.testing import TestCase
from werkzeug.test import Client
from werkzeug.datastructures import Headers
from buildings_app.buildings import buildings
import unittest
import base64

class BuildingsAuthTest(TestCase):
	def create_app(self):
		#views.DATABASE = 'testing.sqlite3'
		#if os.path.exists(views.DATABASE):
		#	os.unlink(views.DATABASE)
		#query_db(self.CREATE_TABLE)
		#return buildings.app
		pass
	
	
	def test_admin_page_is_locked(self):
		rv = self.client.get('/erp/gen/1.0/buildings')

		self.assert_401(rv)
		self.assertTrue('WWW-Authenticate' in rv.headers)
		self.assertTrue('Basic' in rv.headers['WWW-Authenticate'])
	
	def test_admin_page_rejects_bad_username(self):
		h = Headers()
		h.add('Authorization', 'Basic ' + base64.b64encode('foo:my_password'))
		rv = Client.open(self.client, path='/erp/gen/1.0/buildings',
						 headers=h)
		self.assert_401(rv)

	def test_admin_page_allows_valid_login(self):
		h = Headers()
		h.add('Authorization',
			  'Basic ' + base64.b64encode('2144402c-586e-44fc-bd0c-62b31e98394d:'))
		rv = Client.open(self.client, path='/erp/gen/1.0/buildings',
						 headers=h)
		self.assert_200(rv)
			
if __name__ == "__main__":
	#import sys;sys.argv = ['', 'Test.testName']
	unittest.main()	