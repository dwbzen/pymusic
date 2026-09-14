'''
Created on Aug 30, 2026

@author: dwbze
'''

from common.environment import Environment
import json
from typing import List, Set
import argparse

class ScaleLib():
    """ Encapsulates scales and instruments.
    """
    
    SCALES_FILE = "common_scaleFormulas.json"
    
    def __init__(self, scales_filename:str=None):
        env = Environment.get_environment()
        resource_folder = env.get_resource_folder("music")
        self.scales_file_name = ScaleLib.SCALES_FILE if scales_filename is None else scales_filename
        self.scales_file = f"{resource_folder}/{self.scales_file_name}"
        with open(self.scales_file, "r") as read_file:
            scales_data = json.load(read_file)
        
        # index the scales by both the name and all the alternate names
        # save the scale names as a property
        self._scaleLib = {}
        self._scalesData = scales_data["scales"]   # List[dict] from the scales JSON file
        self._scaleNames = []
        for scale in self._scalesData:
            name = scale["name"]
            self._scaleNames.append(name)
            self._scaleLib[name] = scale
            self._scaleLib[name.lower()] = scale
            alt_names = scale.get("alternateNames", [])
            for alt_name in alt_names:
                self._scaleNames.append(alt_name)
                self._scaleLib[alt_name] = scale
                self._scaleLib[alt_name.lower()] = scale
        self._scaleNames.sort()

        # extract and save all the group names
        self._groupNames = set()
        for scale in self._scalesData:
            for group in scale["groups"]:
                self._groupNames.add(group)

    
    def getScaleData(self, scale_name)->dict|None:
        """ Returns the scale data (as a dict) for the scale name provided
            Argument:
                scale_name - a valid scale name 
            Returns None if there is no scale with that name.
            Example: getScaleData("Major) returns the dict  { "name" : "Major","groups" : ["major", "diatonic", "common"],"formula" : [2,2,1,2,2,2,1],"size" : 7},
        """
        scale_data = self.scaleLib.get(scale_name, None)
        if scale_data is None:
            scale_data = self.scaleLib.get(scale_name.lower(), None)
        return scale_data
    
    @property
    def scaleLib(self)->dict:
        return self._scaleLib
    
    @property
    def groupNames(self)->Set(str):
        return self._groupNames
    
    @property
    def scaleNames(self)->List[str]:
        return self._scaleNames
    
    @property
    def scalesData(self)->List[dict]:
        return self._scalesData
    
    @property
    def instruments(self)->dict:
        return self._instruments
    
    @property
    def instrument_names(self)->List[str]:
        return self._instrument_names
    
    def toJson(self, indent:int=None, sort_keys=True)->str:
        js = json.dumps(self.scaleLib, indent=indent, sort_keys=sort_keys)
        return js
    

def main():
    description = "Create a library of scales from a JSON scales file"
    parser = argparse.ArgumentParser(prog="ScaleLib", description=description)
    parser.add_argument("filename", help="Scale JSON file", type=str, default=None)
    parser.add_argument("--name", "-N", help="Scale name", type=str, default="Dorian")
    args = parser.parse_args()
    
    print(f"scales JSON file: {args.filename}")
    sclib = ScaleLib(args.filename)
    print(f"scaleLib: {sclib.toJson()}")
    print(f"scale names: {sclib.scaleNames}")
    scaledata = sclib.getScaleData(args.name)
    print(f"Lydian b7: {scaledata}")
    
if __name__ == '__main__':
    main()