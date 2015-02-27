'''
Created on Sep 22, 2014

@author: dennis
'''

from config import config
import logging.config
import cx_Oracle
from optparse import OptionParser

class HoldModel():
	
	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('hold_model')
		self.log.info('init() initializing HoldModel')
			

	def verify_authorization(self, advisor_psuid):
		'''
			Verify the given advisor is authorized to clear advising holds
			
			@type	advisor_psuid: string
			@param	advisor_psuid: the '9'-number of the advisor to check for authorization
			@rtype string
			@return one of 'true', 'false', or 'dne' for the case of authorized, unauthorized, and person does not exist
		'''
		try:
			self.log.debug('verify_authorization():model: verifying advising hold authorization for: ' + advisor_psuid)
			is_authorized = 'false'

			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.hold_db_user, config.hold_db_password, dsn)
			cursor = db.cursor()
						
			self.log.info('verify_authorization():model: verifying authorization to clear holds from db for person: ' + advisor_psuid)
			is_authorized = 'true'

			is_authorized = cursor.callfunc('zskadvpt.f_advisingHoldClearAuth', cx_Oracle.STRING, [advisor_psuid])

			self.log.info('verify_authorization():model: verifying authorization to clear advising holds, result: ' + str(is_authorized))
			
			db.close()

		except Exception as ex:
			self.log.error('verify_authorization():model: error: ' + str(ex))
	
		self.log.info('verify_authorization():model: returning verification status of: ' + advisor_psuid + ' as: ' + is_authorized )
		return(is_authorized)

	def get_advising_hold(self, student_psuid):
		'''
			Get the advising hold status for the given student
			
			@type	student_psuid: string
			@param	student_psuid: the '9'-number of the student to check for advising hold
			@rtype string
			@return one of 'true', 'false', or 'dne' for the case of has hold, does not have hold, and person does not exist
		'''
		try:
			self.log.debug('get_advising_hold():model: getting the advising hold status for: ' + student_psuid)
			has_hold = 'true'

			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
						
			self.log.info('get_advising_hold():model: getting the advising hold status from db for person: ' + student_psuid)
			has_hold = 'false'
			has_hold = cursor.callfunc('zskadvpt.f_advisingHoldCheck', cx_Oracle.STRING, [student_psuid])

			self.log.info('get_advising_hold():model: advising hold status from banner: ' + str(has_hold))
			
			db.close()

		except Exception as ex:
			self.log.error('get_advising_hold():model: error: ' + str(ex))
	
		self.log.info('get_advising_hold():model: returning advising hold status of: ' + student_psuid + ' as: ' + has_hold )
		return(has_hold)


	def clear_advising_hold(self, advisor_psuid, student_psuid):
		'''
			Clear the advising hold status for the given student
			
			@type	advisor_psuid: string
			@param	advisor_psuid: the '9'-number of the advisor clearing the advising hold
			@type	student_psuid: string
			@param	student_psuid: the '9'-number of the student to have advising hold cleared
			@rtype string
			@return one of 'true', 'false', or 'dne' for the case of has hold, does not have hold, and person does not exist
		'''
		try:
			self.log.debug('clear_advising_hold():model: getting the advising hold status for: ' + student_psuid)
			is_cleared = 'true'

			dsn = cx_Oracle.makedsn(*config.database_dsn)
			db = cx_Oracle.connect(config.lms_login, config.lms_password, dsn)
			cursor = db.cursor()
						
			self.log.info('clear_advising_hold():model: clearing advising hold from db for person: ' + student_psuid)
			is_cleared = 'false'
			is_cleared = cursor.callfunc('zskadvpt.f_advisingHoldClear', cx_Oracle.STRING, [advisor_psuid, student_psuid])

			self.log.info('clear_advising_hold():model: advising hold status from banner: ' + str(is_cleared))
			
			db.close()

		except Exception as ex:
			self.log.error('clear_advising_hold():model: error: ' + str(ex))
	
		self.log.info('clear_advising_hold():model: returning advising hold status of: ' + student_psuid + ' as: ' + is_cleared )
		return(is_cleared)


if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	parser.add_option("-f", "--fore", dest="fore", action='store_true', default=False, help="Run as a foreground process instead of a daemon")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
		pass

