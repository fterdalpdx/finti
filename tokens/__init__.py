from flask import Flask
#from flask.ext.bootstrap import Bootstrap
from config import config
from . import tokens

def create_app():
	app = Flask(__name__)
	app.config.from_object(config)
	config.init_app(app)
	#tokens.Tokens.init_app(app)
	
#	Bootstrap.init_app(app)
	from web import web as web_blueprint
	app.register_blueprint(web_blueprint)
	
	return app