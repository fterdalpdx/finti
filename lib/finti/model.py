'''
Created on Sep 22, 2014

@author: dennis
'''

from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
import os
import pprint
from config import Properties
import logging.config

prop = Properties()
logging.config.dictConfig(prop.logging_conf_dict)
log = logging.getLogger('buildings')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(prop.db_path, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

class Building(db.Model):
	__tablename__ = 'buildings'
	building_identifier = db.Column(db.String(6), primary_key=True)
	long_name = db.Column(db.String(60), nullable=False)
	short_name = db.Column(db.String(30), nullable=False)
	building_code = db.Column(db.String(6), index=True, nullable=False)
	street_address = db.Column(db.String(75), nullable=False)
	city = db.Column(db.String(50), default='Portland')
	state_code = db.Column(db.String(3), default='OR')
	zipcode = db.Column(db.String(30))
	longitude = db.Column(db.Float)
	latitude = db.Column(db.Float)
	
	def __repr__(self):
		result = {	'building_identifier': self.building_identifier,
			'long_name': self.long_name,
			'short_name': self.short_name,
			'building_code': self.building_code,
			'street_address': self.street_address,
			'city': self.city,
			'state_code': self.state_code,
			'zipcode': self.zipcode,
			'longitude': self.longitude,
			'latitude': self.latitude }
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
			'longitude': bldg.longitude,
			'latitude': bldg.latitude }
		#return '<Building %r>' % bldg.building_code
		return result

def init_db():
	db.drop_all()
	add_default_data(db)
		
def add_default_data(db):
	db.create_all()
	AB = Building(building_identifier='B0039A', long_name='Art Building', short_name='Art Bldg',
				building_code='AB', street_address='2000 SW 5TH AVE', zipcode='97219',
				longitude=-122.682749, latitude=45.508593)

	EB = Building(	building_identifier='B0038',
				long_name='Engineering Building',
				short_name='Engineering Bldg',
				building_code='EB',
				street_address='1930 SW FOURTH AVENUE',
				zipcode='97219',
				longitude=-122.681008,
				latitude=45.50898)
	db.session.add_all([AB,EB])
	db.session.commit()
	
def add_building(building):
	status = False
	try:
		bldg = Building(**building)
		db.session.add(bldg)
		db.session.commit()
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
		status = True
	except Exception as ex:
		db.session.rollback()
		log.debug('update_building(): error: ' + str(ex))

	return(status)

def get_building(building_identifier):
	bldg = None
	try:
		bldg_res = Building.query.filter_by(building_identifier = building_identifier).all()
		if bldg_res > 0:
			bldg = conv_building(bldg_res[0])
		else:
			bldg = None
	except Exception as ex:
		log.debug('get_building(): error: ' + str(ex))

	return(bldg)

def list_buildings():
	bldgs = []
	try:
		bldg_list = Building.query.all()
		for bldg in bldg_list:
			bldgs.append(conv_building(bldg))
	except Exception as ex:
		log.debug('list_building(): error: ' + str(ex))

	return(bldgs)
	