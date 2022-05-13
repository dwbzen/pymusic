
from threading import Lock

class Environment(object):
    _environ = None
    _lock = Lock()
    
    def __init__(self, package_name):
        self.resource_base = '/Compile/dwbzen/resources'
        self.package_name = package_name
        self.resources = {}
        self.resources['music'] = self.resource_base + '/music'
        self.resources['text'] = self.resource_base + '/text'
        self.items = {}
        
    def __repr__(self):
        return '<Environment>'
        
    def get_resource_folder(self, package):
        if package in self.resources:
            return self.resources[package]
        else:
            return self.resource_base

    def add_item(self, key, value):
        self.items[key] = value
    
    def get_items(self):
        return self.items
    
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

