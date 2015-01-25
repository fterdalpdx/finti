'''
Created on Jan 25, 2015

@author: dennis
'''
import unittest
import os
import re

class TestAll(unittest.TestCase):
    

    def suite(self):
        files = os.listdir('.')
        test_files_re = re.compile("test\.py$", re.IGNORECASE)
        files = filter(test_files_re.search, files)
        filenameToModuleName = lambda f: os.path.splitext(f)[0]
        moduleNames = map(filenameToModuleName, files)
        modules = map(__import__, moduleNames)
        load = unittest.defaultTestLoader.loadTestsFromModule
        return unittest.TestSuite(map(load, modules))
    
        #building_auth = unittest.TestLoader().loadTestsFromModule('buildings_auth')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(defaultTest='suite')