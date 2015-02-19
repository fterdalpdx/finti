'''
Created on Sep 23, 2014

@author: dennis
'''

import logging.config
from config import config
import vote_app.vote_model
from optparse import OptionParser
from cats import here_kitty

class Vote():
	'''
		Encapsulates the PSU student election voter verification service.
	'''

	def __init__(self):
		logging.config.dictConfig(config.logging_conf_dict)
		self.log = logging.getLogger('vote')
		self.log.debug('init(): starting')
		self.model = vote_app.vote_model.VoteModel()
	
	def verify_eligibility(self, odin_name):
		'''
			Check whether or not the given person is eligible to vote in the ASPSU student elections
		'''
		status = {
				'error': {
						'message':	'The student could not be found.',
						'type':		config.people_err_dne,
						'cat':		here_kitty()
				}
		}
		
		is_eligible = self.model.verify_eligibility(odin_name)
		if is_eligible == 'true':
			status = {'success': {'voter': 'true'}}
			self.log.info('verify_eligibility(): student is eligible to vote in student election: ' + odin_name)
		elif is_eligible == 'false':
			status = {'success': {'voter': 'false'}}
			self.log.info('verify_eligibility(): student is ineligible to vote in student election: ' + odin_name)
		elif is_eligible == 'dne':
			self.log.info('verify_eligibility(): student did not exist in lookup in banner: ' + odin_name)
		else:
			self.log.error('verify_eligibility(): unexpected result from verify_eligibility request: ' + is_eligible)
		
		return status
	
	
vote = Vote()

if __name__ == '__main__':	
	parser = OptionParser()
	parser.add_option("-D", "--debug", dest="debug", action='store_true', default=False, help="Run in debug mode")
	
	(options, args) = parser.parse_args()
	
	if not options.debug:
		pass
	#	context = daemon.DaemonContext(umask=0o002)
	#	with context:




		