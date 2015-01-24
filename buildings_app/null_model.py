'''
Created on Sep 22, 2014

@author: dennis
'''

from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
import os
import pprint
from config import config
import logging.config
import redis
from beaver.transports.base_transport import json

logging.config.dictConfig(config.logging_conf_dict)
log = logging.getLogger('model')

if config.buildings_cache_enabled == True:
	redis = redis.StrictRedis(db=config.buildings_cache_redis_db)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(config.db_path, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

class Building(db.Model):
	__tablename__ = 'buildings_app'
	building_identifier = db.Column(db.String(6), primary_key=True)
	long_name = db.Column(db.String(60), nullable=False)
	short_name = db.Column(db.String(30), nullable=False)
	building_code = db.Column(db.String(6), index=True, nullable=False)
	street_address = db.Column(db.String(75), nullable=False)
	city = db.Column(db.String(50), default='Portland')
	state_code = db.Column(db.String(3), default='OR')
	zipcode = db.Column(db.String(30))
	rlis_lat = db.Column(db.Float)
	rlis_long = db.Column(db.Float)
	geolocate_lat = db.Column(db.Float)
	geolocate_long = db.Column(db.Float)
	centroid_lat = db.Column(db.Float)
	centroid_long = db.Column(db.Float)
	
	def __repr__(self):
		result = {	'building_identifier': self.building_identifier,
			'long_name': self.long_name,
			'short_name': self.short_name,
			'building_code': self.building_code,
			'street_address': self.street_address,
			'city': self.city,
			'state_code': self.state_code,
			'zipcode': self.zipcode,
			'rlis_lat': self.rlis_lat,
			'rlis_long': self.rlis_long,
			'geolocate_lat': self.geolocate_lat,
			'geolocate_long': self.geolocate_long,
			'centroid_lat': self.centroid_lat,
			'centroid_long': self.centroid_long
		}
		#return '<Building %r>' % self.building_code
		return str(result)
	
def conv_building(bldg):
		result = {	'building_identifier': bldg.building_identifier,
			'long_name': bldg.long_name,
			'short_name': bldg.short_name,
			'building_code': bldg.building_code,
			'street_address': bldg.street_address,
			'city': bldg.city,
			'state_code': bldg.state_code,
			'zipcode': bldg.zipcode,
			'rlis_lat': bldg.rlis_lat,
			'rlis_long': bldg.rlis_long,
			'geolocate_lat': bldg.geolocate_lat,
			'geolocate_long': bldg.geolocate_long,
			'centroid_lat': bldg.centroid_lat,
			'centroid_long': bldg.centroid_long
		}
		#return '<Building %r>' % bldg.building_code
		return result

def init_db():
	db.drop_all()
	add_default_data(db)
		
def add_default_data(db):
	db.create_all()
	AB = Building(building_identifier='B0039A', long_name='Art Building', short_name='Art Bldg',
				building_code='AB', street_address='2000 SW 5TH AVE', zipcode='97219',
				rlis_lat=45.508593, rlis_long=-122.682749, 
				geolocate_lat=45.508593, geolocate_long=-122.682749, 
				centroid_lat=45.508593, centroid_long=-122.682749) 

	EB = Building(	building_identifier='B0038',
				long_name='Engineering Building',
				short_name='Engineering Bldg',
				building_code='EB',
				street_address='1930 SW FOURTH AVENUE',
				zipcode='97219',
				rlis_lat=45.50898, rlis_long=-122.681008,
				geolocate_lat=45.50898, geolocate_long=-122.681008,
				centroid_lat=45.50898, centroid_long=-122.681008)
				
	db.session.add_all([AB,EB])
	db.session.commit()
	
	
def add_building(building):
	status = False
	try:
		bldg = Building(**building)
		db.session.add(bldg)
		db.session.commit()
		if config.buildings_cache_enabled == True:
			building_json = json.dumps(building)
			building_id = building['building_identifier']
			redis.set(building_id, building_json, ex=config.buildings_cache_ttl)
			#redis.del('buildings_app')	# invalidate the buildings_app collection cache entry
		status = True
	except Exception as ex:
		db.session.rollback()
		log.debug('add_building(): error: ' + str(ex))

	return(status)
		
def remove_building(building_identifier):
	status = False
	try:
		bldg = Building.query.filter_by(building_identifier = building_identifier).all()[0]
		db.session.delete(bldg)
		db.session.commit()
		if config.buildings_cache_enabled == True:
			redis.delete(building_identifier)
			redis.delete('buildings_app')
		status = True
	except Exception as ex:
		db.session.rollback()
		log.debug('remove_building(): error: ' + str(ex))
	return(status)
		
def update_building(building):
	status = False
	try:
		bldg = Building.query.filter_by(building_identifier = building['building_identifier']).all()[0]
		for k,v in building.items():
			setattr(bldg, k, v)
		db.session.add(bldg)
		db.session.commit()
		if config.buildings_cache_enabled == True:
			building_json = json.dumps(building)
			building_id = building['building_identifier']
			redis.set(building_id, building_json, ex=config.buildings_cache_ttl)
			redis.delete('buildings_app')	# invalidate the buildings_app collection cache entry
		status = True
	except Exception as ex:
		db.session.rollback()
		log.debug('update_building(): error: ' + str(ex))

	return(status)

def get_building(building_identifier):
	building = None
	try:
		if config.buildings_cache_enabled == True:
			building_json = redis.get(building_identifier)
			if building_json is not None:
				building = json.loads(building_json)
				return building

		bldg_res = Building.query.filter_by(building_identifier = building_identifier).all()
		
		if bldg_res > 0:
			building = conv_building(bldg_res[0])
			if config.buildings_cache_enabled == True:
				building_json = json.dumps(building)
				redis.set(building_identifier, building_json, ex=config.buildings_cache_ttl)
		else:
			building = None
	except Exception as ex:
		log.debug('get_building(): error: ' + str(ex))

	return(building)

def list_buildings():
	bldgs = []
	try:
		if config.buildings_cache_enabled == True:
			buildings_json = redis.get('buildings_app')
			if buildings_json is not None:
				buildings = json.loads(buildings_json)
				return buildings

		bldg_list = Building.query.all()
		for bldg in bldg_list:
			bldgs.append(conv_building(bldg))

		if config.buildings_cache_enabled == True:
			buildings_json = json.dumps(buildings)
			redis.set('buildings_app', buildings_json, ex=config.buildings_cache_ttl)

	except Exception as ex:
		log.debug('list_building(): error: ' + str(ex))

	return(bldgs)
	