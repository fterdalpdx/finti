import os

def application(environ, start_response):
	for var in ['RELEASE_LEVEL']:
		os.environ['key'] = environ.get(key,'')
		
	from health_app.get_instance import app
	
	return app(environ, start_response)
