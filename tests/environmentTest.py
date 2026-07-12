'''
Created on Oct 14, 2025

@author: don_bacon
'''

import unittest
from common.environment import Environment

class Test(unittest.TestCase):


    def test_environment(self):
        print(f"\n****** test_environment for music package ==========================")
        env = Environment("music")
        print(f"pure path: {env.pure_path}")
        
        print(f"resource base: {env.resource_base}")
        print(f"package base: {env.package_base}")
        print(f"resources: {env.resources}")
        #print(f"data: {env.data}")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testEnvironment']
    unittest.main()