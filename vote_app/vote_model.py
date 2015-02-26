'''
Created on Sep 22, 2014

@author: dennis
'''

from config import config
import logging.config
import cx_Oracle
from optparse import OptionParser

class VoteModel():
	
	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('vote_model')
		self.log.info('init() initializing VoteModel')
		self.dsn = cx_Oracle.makedsn(*config.database_dsn)
			

	def verify_eligibility(self, odin_name):
		'''
			Lookup voting eligibility in banner for given person
			
			@type	odin_name: string
			@param	odin_name: the odin login name for the student to verify
			@rtype string
			@return one of 'true', 'false', or 'dne' for the case of voting eligibile, voting ineligible, and person does not exist
		'''
		try:
			self.log.debug('verify_eligibility(): verifying voting eligibility for: ' + odin_name)
			is_eligible = 'db error'

			db = cx_Oracle.connect(config.lms_login, config.lms_password, self.dsn)
			cursor = db.cursor()
						
			self.log.info('verify_eligibility(): verifying eligibility to vote from db for person: ' + odin_name)
			is_eligible = cursor.callfunc('f_eligible2vote', cx_Oracle.STRING, [odin_name])
			
			self.log.info('verify_eligibility(): verifying eligibility to vote from db, result: ' + str(is_eligible))
			
			db.close()

		except Exception as ex:
			self.log.error('verify_eligibility(): error: ' + str(ex))
	
		self.log.info('verify_eligibility(): returning verification status of: ' + odin_name + ' as: ' + is_eligible )
		return(is_eligible)

if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	parser.add_option("-f", "--fore", dest="fore", action='store_true', default=False, help="Run as a foreground process instead of a daemon")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
		pass

