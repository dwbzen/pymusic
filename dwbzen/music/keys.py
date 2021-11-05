# ------------------------------------------------------------------------------
# Name:          keys.py
# Purpose:       Encapsulate music keys.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import music
from music21 import key
import pandas as pd

class Keys(object):


    def __init__(self, verbose=0, resource_folder ="/Compile/dwbzen/resources/music"):
        
        self.resource_folder = resource_folder
        self.keys_file = resource_folder + "/keys.json"
        self.verbose = verbose
        self.keys_pd = pd.read_json(self.keys_file, orient="index")
        self.keys_pd.fillna(value={'parallelKey':'0'}, inplace=True)

    if __name__ == '__main__':
        keys = music.Keys()
        print(keys.keys_pd)

