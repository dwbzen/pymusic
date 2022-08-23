
from threading import Lock

class Environment(object):
    _environ = None
    _lock = Lock()
    
    def __init__(self, package_name):
        """Initialize the running Environment by setting global environment variables
        
        TODO: implement using a properties config file
        
        """
        self.name = package_name
        self.resource_base = '/Compile/dwbzen/resources'    # for managed resources
        self.data_base = '/Compile/dwbzen/data'             # for output files
        self.package_name = package_name
        self.resources = {}
        self.data = {}
        self.resources['music'] = self.resource_base + '/music'
        self.resources['text'] = self.resource_base + '/text'
        self.data['music'] = self.data_base + '/music'
        self.data['text'] = self.data_base + '/text'
        self._items = {}
        
    def __repr__(self):
        return '<Environment>'
        
    def get_resource_folder(self, package):
        if package in self.resources:
            return self.resources[package]
        else:
            return self.resource_base
    
    def get_data_folder(self, package):
        if package in self.resources:
            return self.data[package]
        else:
            return self.data_base
        
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

