'''
Created on Feb 1, 2015

@author: dennis
'''

import logging
from config import config
import requests

class PushbulletHandler(logging.StreamHandler):
    """
    A handler class which sends messages to a Pushbullet target
    """

    def emit(self, record):
        try:
            msg = self.format(record)
            title = record.levelname + ': ' + record.funcName
            data=dict(title=title, body=msg, type='note')
            requests.post('https://api.pushbullet.com/api/pushes', auth=(config.pushbullet_api_token,''), data=data)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
