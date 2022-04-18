'''
Created on Mar 3, 2021

@author: don_bacon
'''
import json
from music.scale import Scale

class Chord(object):

    def __init__(self, raw_data={}):
        '''
        Constructor
        '''
        # print("raw data: {}".format(raw_data))
        if(type(raw_data) is dict):
            self.chord = raw_data
        else:
            self.chord = json.loads(raw_data)
    
        self.name = self.chord['name']
        self.formula = self.chord['formula']
        self.intervals = self.chord['intervals']
        self.notes = self.chord['spelling'].split(' ')
        self.symbols = self.chord['symbols']
        self.size = len(self.formula)
        _scale = {}
        _scale['formula'] = self.formula
        _scale['name'] = self.name
        self.scale = Scale(_scale)
        
