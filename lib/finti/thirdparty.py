'''
Created on Aug 26, 2014

@author: dennis
'''
import flask
from flask import request, session
from flask import Flask
import requests
import json

# This class will be defined later in this post 

from lib.finti.provider import PSUAuthorizationProvider

app = Flask(__name__)

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'


client_id = '314'
user_id='rincewind'
client_secret = 'octarine'
finish_redirect_uri = 'http://localhost:5000/thirdparty'

@app.route("/thirdparty", methods=["GET"])
def thirdparty_worker():
	code = request.args.get('code')
	#team_id = request.args.get('team_id')
	#print('thirdparty_worker() code: ' + code + ', team_id: ' + team_id )
	print('thirdparty_worker() code: ' + str(code) )
	

	form_data = {	"code": code,
					"grant_type": 'authorization_code',
					"client_id": client_id,
					"client_secret": client_secret,
					"redirect_uri": finish_redirect_uri }

	r = requests.request('POST', 'http://localhost:5001/v1/oauth2/token', data=form_data )

	if r.ok == True:
		text = json.loads(r.text)
		access_token = text['access_token']
		refresh_token = text['refresh_token']
		print('thirdparty_worker() post post and result ok, access_token: ' + access_token)
	else:
		print('thirdparty_worker() post post and result fail: ' + r.text)
	
	data = {'access_token': access_token}
	headers = {'Authorization': 'Bearer ' + access_token}

	r = requests.request('GET', 'http://localhost:5002/protected/resource', headers=headers )

	if r.ok == True:
		print('thirdparty_worker() access request result: ' + r.text)
	else:
		print('thirdparty_worker() access request failed')

	return str(request)


if __name__ == '__main__':
	app.run(debug=True)