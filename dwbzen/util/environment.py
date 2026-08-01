
'''
Created on Jan 7, 2025

@author: don_bacon
'''


from threading import Lock
import sys, os

class Environment(object):
    _environ = None
    _lock = Lock()
    
    def __init__(self, package_name=None):
        """Initialize the running Environment by setting global environment variables
        """
        self.game_path = os.path.dirname(os.path.abspath(__file__))    # for example "C:\Compile\Utils\util\"
        # print(f" game_path: {self.game_path}")
    
        self.resource_base = os.path.join(self.game_path, '..', 'resources')
        self.package_base = os.path.join(self.game_path, '..')

        self.name = package_name
        self.package_name = package_name
        self.resources = {}
        self.items = {}
        
    def __repr__(self):
        return '<Environment>'
    
    
    def get_resource_folder(self, package=None):
        if package is None:
            return self.resource_base
        if package in self.resources:
            return self.resources[package]
        else:
            print(f'Invalid package {package}', file=sys.stderr)
            return None

    def add_item(self, key, value):
        self.items[key] = value
    
    def get_items(self):
        return self.items
    
    def get_item(self, key):
        return self.items[key]

    @classmethod
    def get_environment(cls):
        env = None
        cls._lock.acquire()
        if cls._environ is not None:
            env = cls._environ
        else:
            cls._environ = Environment('util')
            env = cls._environ
        cls._lock.release()
        return env

