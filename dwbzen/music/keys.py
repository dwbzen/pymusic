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
from music.key import Key
from music21 import key, note, pitch
from typing import List
import json

class Keys(object):
    """ Keys can be provided in keys.json in the project resource folder (the default), or
        as a dict having the same structure.
        The complete set has 30 keys: 15 major, and 15 minor.
        Each has 8 sharp keys and 7 flat keys, completing the Circle of 5ths.
    """

    KEYS_FILE = "keys.json"

    def __init__(self, keysfilename:str=None, keys_data:dict={}):
        """Create Keys from a JSON keys file or dictionary
        """
        env = Environment.get_environment()
        resource_folder = env.get_resource_folder("music")
        
        self.resource_folder = resource_folder
        self.keys_file_name = Keys.KEYS_FILE if keysfilename is None else keysfilename
        self.keys_file = f"{resource_folder}/{self.keys_file_name}"
        
        if len(keys_data) > 0 and "key_names" in keys_data and "keys" in keys_data:
            self.keys_data = keys_data
        else:
            self.keys_data = self._get_keys_data()
            
        self.keys = self.keys_data["keys"]
        self.key_names = self.keys_data["key_names"]
        # add keys to alternate_name
        alternate_name_keys = {}
        for k in self.keys:   # iterate of the dict keys which is the name of the Key (confusing but 'key' has 2 meanings
            thekey = self.keys[k]
            alt_name = thekey.get("alternate_name", k)
            alternate_name_keys[alt_name] = thekey
        self.keys.update(alternate_name_keys)
    
    def _get_keys_data(self)->dict:
        with open(self.keys_file, "r") as read_file:
            keys_data = json.load(read_file)
        return keys_data

    def get_key(self, keyname:str)->dict:
        """ Get a Key by name or alternate_name
            Arguments: name - the key name to get. The format is <root>-<mode> where mode is "Major" | "Minor"
                and root is a valid pitch using # for sharp and b for flat if needed.
                If there is no dash in key name the mode is based on the case of the root pitch:
                upper for Major, lower for Minor. 
                The alternate_name is equivalent to str of the associated music21.key.Key.
        """
        return self.keys.get(keyname)
    
    def key(self, keyname:str)->Key:   # returns a Key object
        return Key(self.get_key(keyname))
    
    def get_keys(self)->dict:
        return self.keys


if __name__ == '__main__':
    #print(Keys.__doc__)
    keys = Keys()
    #print(json.dumps(keys.get_keys(), indent=2))
    k = keys.key("F#-Major")    # returns a Key
    print(f"{k.key_name}: mode: {k.mode}, signature: {k.get_key_signature()}")
    print(f"{k.key_name}: mode: {k.mode}, signature: {k.get_key_signature(False)}")
    
    k = keys.key("Bb-Minor")    # returns a Key
    print(f"{k.key_name}: mode: {k.mode}, signature: {k.get_key_signature()}")
    print(f"{k.key_name}: mode: {k.mode}, signature: {k.get_key_signature(False)}")
    
    k = keys.key("b- minor")    # alternate name
    print(f"names: '{k.key_name}', '{k.alternate_name}': mode: {k.mode}, accidental: {k.accidental}, signature: {k.get_key_signature()}")
    


