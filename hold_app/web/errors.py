from flask import jsonify, make_response
from . import web

@web.app_errorhandler(400)
def custom_400(error):
	return make_response(jsonify(error.description), 400)

@web.app_errorhandler(404)
def custom_404(error):
	return make_response(jsonify(error.description), 404)

