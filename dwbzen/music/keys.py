'''
Created on Feb 18, 2021

@author: don_bacon
'''
import json
import pandas as pd

class Keys:
    '''
    Represents JSON format Keys: keys.json
    '''

    def __init__(self, raw_data={}, json_file_name=''):
        '''
        Constructor
        '''
        self.keys = []
        self.key = {}
        self.key_names = []
        if (len(json_file_name) >0):
            _song_file = json_file_name
            with open(_song_file, "r") as read_file:
                self.data = json.load(read_file)
        else:
            self.data = raw_data
        self._get_keys_data()

    def _get_keys_data(self):
        self.keys = self.data['keys']
        for k in self.keys:
            self.key_names.append(k['name'])
            self.key[k['name']] = k
    
        self.df_keys = pd.DataFrame(self.keys)
        self.df_keys = self.df_keys.fillna(value={'parallelKey':'0'})
