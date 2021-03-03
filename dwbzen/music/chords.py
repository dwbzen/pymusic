'''
Created on Mar 2, 2021

@author: don_bacon
'''
import music
import json
from pandas.core.frame import DataFrame

class Chords(object):
    '''
    Chord formulas
    '''


    def __init__(self, raw_data={}, json_file_name=''):
        '''
        Constructor
        '''
        self.chords = {}
        self.chord = {}
        self.chords_file = ''
        self.data = {}
        self.chord_names = []
    
    def get_chords_data(self):
        pass
    
    def __iter__(self):
        ''' Iterate over the scales '''
        return self.chords.__iter__()
    