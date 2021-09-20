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
        if (len(json_file_name) >0):
            self.chords_file = json_file_name
            with open(self.chords_file, "r") as read_file:
                self.data = json.load(read_file)
        else:
            self.data = raw_data
            
        self.get_chords_data()
    
    def get_chords_data(self):
        self.chords = self.data['chordFormulas']
        for s in self.chords:
            self.chord_names.append(s['name'])
            self.chord[s['name']] = music.Chord(s)
        self.df_chords = DataFrame(self.chords)
    
    def __iter__(self):
        ''' Iterate over the chords '''
        return self.chords.__iter__()

        
        

    