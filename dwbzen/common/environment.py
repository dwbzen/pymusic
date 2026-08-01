
from threading import Lock
import os, sys, argparse
from pathlib import PurePath
from textwrap import dedent
from typing import Dict

class Environment(object):
    _environ = None
    _lock = Lock()
    
    def __init__(self, _project_name, data_path="data"):
        """ Initialize the running Environment by setting global environment variables.
            Assumes that all project  resources are in the folder <project_name>/resources.
            Arguments:
                project_name - Python project name. If None, it uses the last element of the path to
                    this file (the project base path) as the project name.
                data_path - project output folder name. Default is "data", path is <project_name>/data
            resource subfolder names (aka packages) are automatically determined and saved in 
            the dict, self.resources: Dict[package_name, full path]
        """
        self.env_path = os.path.dirname(os.path.abspath(__file__))    # __file__ is the path of this file (environment.py)
        self.project_base = os.path.normpath(os.path.join(self.env_path, '..', '..'))
        project_name = self.project_base.split("\\")[-1] if _project_name is None else _project_name
        
        self.name = project_name
        self.project_name = project_name


        self.pure_path = PurePath(self.project_base)
        
        self.resource_base = os.path.normpath(os.path.join(self.env_path, '..', '..', 'resources'))    # for managed resources
        self.data_base = os.path.normpath(os.path.join(self.env_path, '..', '..', data_path))         # for output files
        
        resource_dirs = os.listdir(self.resource_base)
        #
        # parse out the resources subfolders
        #
        self.resources = {}
        self.data = {}
        for p in resource_dirs:
            pkg = os.path.join(self.resource_base, p)
            if os.path.isdir(pkg):
                self.resources[p] = os.path.normpath(pkg)
                self.data[p] =  os.path.normpath(os.path.join(self.data_base, p))
        
        self._items = {}
        
    def __repr__(self):
        return '<Environment>'
    
    def get_resources(self)->Dict[str,str]:
        return self.resources
    
    def get_project_base(self)->str:
        return self.project_base
        
    def get_env_path(self)->str:
        return self.env_path
        
    def get_resource_folder(self, package=None):
        if package is None:
            return self.resource_base
        if package in self.resources:
            return self.resources[package]
        else:
            print(f'Invalid package {package}', file=sys.stderr)
            return None
    
    def get_data_folder(self, package=None)->str:
        if package is None:
            return self.data_base
        if package in self.resources:
            return self.data[package]
        else:
            print(f'Invalid package {package}', file=sys.stderr)
            return None
    
    def get_data_folders(self)->dict:
        return self.data
        
    def add_item(self, key, value):
        self.items[key] = value
    
    @property
    def items(self):
        return self._items
    
    def get_item(self, key):
        return self.items[key]

    @staticmethod
    def get_environment(project_name="dwbzen"):
        env = None
        Environment._lock.acquire()
        if Environment._environ is not None:
            env = Environment._environ
        else:
            Environment._environ = Environment(project_name)
            env = Environment._environ
        Environment._lock.release()
        return env
    
def main():
    description = dedent("""
    Display the current environment.
    """)
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", "-p",  help="project name, defaults to None", type=str, default=None)
    parser.add_argument("--package", help="name of the package under resources folder", type=str, default=None)
    args = parser.parse_args()
    environment = Environment.get_environment(args.project)
    print(f"resources: {environment.get_resources()}")
    print(f"project base: {environment.get_project_base()}")
    print(f"resources base: {environment.get_resource_folder()}")
    if args.package is not None:
        print(f"data folder: {environment.get_data_folder(args.package)}")
    else:
        print(f"data folders: {environment.get_data_folders()}")
    print(f"env path: {environment.get_env_path()}")

if __name__ == '__main__':
    main()
    
