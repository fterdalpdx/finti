'''
Created on Sep 23, 2014

@author: dennis
'''

import logging.config
from config import config
import hold_app.hold_model
#import hold_app.hold_null_model
from optparse import OptionParser
from cats import here_kitty

class Hold():
	'''
		Encapsulates the PSU student election voter verification service.
	'''

	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('hold')
		self.log.debug('init(): starting')
		self.model = hold_app.hold_model.HoldModel()
		#self.model = hold_app.hold_null_model.HoldNullModel()
	
	def verify_authorization(self, psuid):
		'''
			Check whether or not the given advisor is authorized to clear advising holds
		'''
		status = {
				'error': {
						'message':	'The advisor could not be found.',
						'type':		config.people_err_dne,
						'cat':		here_kitty()
				}
		}
		
		is_authorized = self.model.verify_authorization(psuid)
		if is_authorized == 'true':
			status = {'success': {'authorized': 'true'}}
			self.log.info('verify_authorization(): advisor is authorized to clear advising holds: ' + psuid)
		elif is_authorized == 'false':
			status = {'success': {'authorized': 'false'}}
			self.log.info('verify_authorization(): advisor is not authorized to clear advising holds: ' + psuid)
		elif is_authorized == 'dne':
			self.log.info('verify_authorization(): advisor did not exist in lookup in banner: ' + psuid)
		else:
			self.log.error('verify_authorization(): unexpected result from verify_authorization request: ' + is_authorized)
		
		return status
	
	def get_advising_hold(self, psuid):
		'''
			Check whether or not the given student has an advising hold
		'''
		status = {
				'error': {
						'message':	'The student could not be found.',
						'type':		config.people_err_dne,
						'cat':		here_kitty()
				}
		}
		
		has_hold = self.model.get_advising_hold(psuid)
		if has_hold == 'true':
			status = {'success': {'hold': 'true'}}
			self.log.info('get_advising_hold(): advisor is authorized to clear advising holds: ' + psuid)
		elif has_hold == 'false':
			status = {'success': {'hold': 'false'}}
			self.log.info('get_advising_hold(): advisor is not authorized to clear advising holds: ' + psuid)
		elif has_hold == 'dne':
			self.log.info('get_advising_hold(): advisor did not exist in lookup in banner: ' + psuid)
		else:
			self.log.error('get_advising_hold(): unexpected result from get_advising_hold request: ' + has_hold)
		
		return status
	
	def clear_advising_hold(self, advisor_psuid, student_psuid):
		'''
			Check whether or not the given student has an advising hold
		'''
		status = {
				'error': {
						'message':	'The person could not be found.',
						'type':		config.people_err_dne,
						'cat':		here_kitty()
				}
		}
		
		hold_res = self.model.clear_advising_hold(advisor_psuid, student_psuid)
		if hold_res == 'success':
			status = {'success': {'hold': 'cleared'}}
			self.log.info('clear_advising_hold(): advising hold cleared for student: ' + student_psuid)
		elif hold_res == 'not_authorized':
			status = {'success': {'hold': 'not authorized'}}
			self.log.info('clear_advising_hold(): advisor is not authorized to clear advising holds: ' + advisor_psuid)
		elif hold_res == 'dne':
			self.log.info('clear_advising_hold(): advisor or student did not exist in lookup in banner: ' + advisor_psuid + ', or: ' + student_psuid)
		else:
			self.log.error('clear_advising_hold(): unexpected result from clear_advising_hold request: ' + hold_res)
		
		return status
	
	
hold = Hold()

if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
		pass
	#	context = daemon.DaemonContext(umask=0o002)
	#	with context:




		