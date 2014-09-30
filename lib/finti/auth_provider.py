'''
Created on Aug 26, 2014

@author: dennis
'''
import flask
from flask import request, session
from flask import Flask
import requests
#from app import app 

# This class will be defined later in this post 

from lib.finti.provider import PSUAuthorizationProvider

app = Flask(__name__)

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'


client_id = '314'
user_id='rincewind'
client_secret = 'octarine'
finish_redirect_uri = 'http://localhost:5000/thirdparty_auth'

@app.route('/user_auth', methods=["GET"])
def user_auth():
	session['user'] = user_id
	return 'hello ' + user_id


# Authorization Code 
# Returns a redirect header on success 

@app.route("/v1/oauth2/auth", methods=["GET"])
def authorization_code(): 
	# You can cache this instance for efficiency 
	provider = PSUAuthorizationProvider() 
	# This is the important line 
	response = provider.get_authorization_code_from_uri(request.url) 
	# For maximum compatibility, a standard Response object is provided 
	# Response has the following properties: 
	#
	# 	response.status_code 	int 
	# 	response.text 			response body 
	# 	response.headers 		iterable dict-like object with keys and values 
	# 
	# This response must be converted to a type that your application 
	# framework can use and returned. 
	
	#print('session.user: ' + str(session.user))
	flask_res = flask.make_response(response.text, response.status_code) 
	for k, v in response.headers.iteritems(): 
		flask_res.headers[k] = v
	return flask_res 

# Token exchange 
# Returns JSON token information on success 
@app.route("/v1/oauth2/token", methods=["POST"]) 
def token(): 
	print('token() start')
	# You can cache this instance for efficiency 
	provider = PSUAuthorizationProvider() 
	print('token() created provider')
	
	# Get a dict of POSTed form data 
	data = {k: request.form[k] for k in request.form.iterkeys()} 
	print('token() request data: ' + str(data))
	
	# This is the important line 
	response = provider.get_token_from_post_data(data) 
	
	# The same Response object is provided, and must be converted 
	# to a type that your application framework can use and returned. 
	flask_res = flask.make_response(response.text, response.status_code) 
	for k, v in response.headers.iteritems(): 
		flask_res.headers[k] = v 

	print('token() returning: ' + str(flask_res))
	return flask_res

if __name__ == '__main__':
	app.run(debug=True, port=5001)