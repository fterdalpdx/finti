from flask import jsonify, make_response
from . import web

@web.app_errorhandler(400)
def custom_400(error):
	#token.log.info('custom_400(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 400)

@web.app_errorhandler(404)
def custom_404(error):
	#token.log.info('custom_404(): error: ' + str(error))
	return make_response(jsonify( {'message': error.description}), 404)

