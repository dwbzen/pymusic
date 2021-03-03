'''
Created on Feb 22, 2021

@author: don_bacon
'''
import music
import json
from pandas.core.frame import DataFrame

class Scales:
    '''
    Scale formulas for common scales
    '''

    def __init__(self, raw_data={}, json_file_name=''):
        '''
        Constructor
        '''
        self.scales = {}
        self.scale = {}
        self.scales_file = ''
        self.data = {}
        self.scale_names = []
        if (len(json_file_name) >0):
            self.scales_file = json_file_name
            with open(self.scales_file, "r") as read_file:
                self.data = json.load(read_file)
        else:
            self.data = raw_data
            
        self._get_scales_data()
        
    def _get_scales_data(self):
        self.scales = self.data['scales']
        for s in self.scales:
            self.scale_names.append(s['name'])
            self.scale[s['name']] = music.Scale(s)
        self.df_scales = DataFrame(self.scales)

    def __iter__(self):
        ''' Iterate over the scales '''
        return self.scales.__iter__()
        