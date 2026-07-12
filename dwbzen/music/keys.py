# ------------------------------------------------------------------------------
# Name:          keys.py
# Purpose:       Encapsulate music keys.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2026 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from common.environment import Environment
import json

class Keys(object):
    """ Keys can be provided in keys.json in the project resource folder (the default), or
        as a dict having the same structure.
        The complete set has 30 keys: 15 major, and 15 minor.
        Each has 8 sharp keys and 7 flat keys, completing the Circle of 5ths.
    """

    KEYS_FILE = "keys.json"

    def __init__(self, keysfilename:str=None, keys_data:dict={}):
        """Create Keys from data provided or json file  """
        env = Environment.get_environment()
        resource_folder = env.get_resource_folder()
        
        self.resource_folder = resource_folder
        self.keys_file_name = Keys.KEYS_FILE if keysfilename is None else keysfilename
        self.keys_file = f"{resource_folder}/music/{self.keys_file_name}"
        
        if len(keys_data) > 0 and "key_names" in keys_data and "keys" in keys_data:
            self.keys_data = keys_data
        else:
            self.keys_data = self._get_keys_data()
            
        self.keys = self.keys_data["keys"]
        self.key_names = self.keys_data["key_names"]
        
    
    def _get_keys_data(self)->dict:
        with open(self.keys_file, "r") as read_file:
            keys_data = json.load(read_file)
        return keys_data

    def get_key(self, keyname:str)->dict:
        return self.keys.get(keyname)
    
    def key(self, keyname:str):   # returns a Key object
        return Key(self.get_key(keyname))
    
    def get_keys(self)->dict:
        return self.keys

class Key(object):
    """Key represents a single Key as a dict with the Key name as the dictionary key.
        For example: { "name" : "G major",  "mode" : "Major", "signature" : "F#", "scale" : "Major", "relativeKey" : "E-Minor"}
    """
    def __init__(self, key_data:dict):
        self._key_data = key_data
    
    @property
    def key_name(self)->str:
        return self._key_data["name"]
    
    @property
    def mode(self)->str:
        return self._key_data["mode"]
    
    @property
    def signature(self)->str:
        return self._key_data["signature"]
    
    @property
    def scale(self)->str:
        return self._key_data["scale"]
    
    @property
    def relative_key(self)->str:
        return self._key_data["relativeKey"]
    
    @property
    def parallel_key(self)->str:
        return self._key_data.get("parallelKey", "")
    

if __name__ == '__main__':
    print(Keys.__doc__)
    keys = Keys()
    print(json.dumps(keys.get_keys(), indent=2))
    k = keys.key("Eb-Major")    # returns a Key
    print(f"{k.key_name}: {k.signature}")
    
