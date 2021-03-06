import os

def application(environ, start_response):
	for var in ['RELEASE_LEVEL', 'ORACLE_HOME']:
		os.environ[var] = environ.get(var,'')
	from health_app.get_instance import app
	return app(environ, start_response)
