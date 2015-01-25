from flask import make_response, abort, request
from . import web
from config import config
from health_app.health import health


@web.route(config.health_uri_path, methods = ['GET'])
def health_check_status():
	"""
		route and handle health check request
	"""

	health.log.info('health_check_status(): called from remote address: ' + str(request.remote_addr) + ', for end point: ' + str(request.endpoint))
	status = health.check_health_status()

	if status['result'] <> 'success':
		abort(404, status['message'])
	else:
		return(make_response((status['message'], 200, {'Content-Type': 'application/json'})))
