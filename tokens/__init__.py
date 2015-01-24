from flask import Flask
#from flask.ext.bootstrap import Bootstrap
from config import config
from tokens import tokens

def create_app():
	app = Flask(__name__)
	app.config.from_object(config)

	from web import web as web_blueprint
	app.register_blueprint(web_blueprint)
	
	return app