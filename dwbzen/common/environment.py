
from threading import Lock
import os, sys
from pathlib import PurePath

class Environment(object):
    _environ = None
    _lock = Lock()
    
    def __init__(self, project_name):
        """Initialize the running Environment by setting global environment variables
        
        """
        self.name = project_name
        self.project_name = project_name
        self.env_path = os.path.dirname(os.path.abspath(__file__))    # the path to this file
        self.package_base = os.path.join(self.env_path, '..', '..')
        
        self.pure_path = PurePath(self.package_base)
        #p = self.pure_path.parts
        #print(f"parts: {p}")
        
        self.resource_base = os.path.join(self.env_path, '..', '..', 'resources')    # for managed resources
        self.data_base = os.path.join(self.env_path, '..', '..', 'data')             # for output files
        
        self.resources =  {"music" : PurePath(self.resource_base, 'music'), "text" : PurePath(self.resource_base, 'text')}
        self.data = {"music" : self.data_base + '/music', "text" : self.data_base + '/text'}
    
        self._items = {}
        
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
    
    def get_data_folder(self, package=None):
        if package is None:
            return self.data_base
        if package in self.resources:
            return self.data[package]
        else:
            print(f'Invalid package {package}', file=sys.stderr)
            return None
        
    def add_item(self, key, value):
        self.items[key] = value
    
    @property
    def items(self):
        return self._items
    
    def get_item(self, key):
        return self.items[key]

    @staticmethod
    def get_environment():
        env = None
        Environment._lock.acquire()
        if Environment._environ is not None:
            env = Environment._environ
        else:
            Environment._environ = Environment('dwbzen')
            env = Environment._environ
        Environment._lock.release()
        return env

