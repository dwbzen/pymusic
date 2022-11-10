'''
Created on Mar 2, 2021

@author: don_bacon
'''

import json
from music.chord import Chord
import music
import pandas as pd

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
            
        self.df_chords = self._get_chords_data()
    
    def _get_chords_data(self):
        self.chords = self.data['chordFormulas']
        for s in self.chords:
            self.chord_names.append(s['name'])
            self.chord[s['name']] = Chord(s)
        return pd.DataFrame(self.chords)
    
    def get_chords(self):
        return self.df_chords
    
    def __iter__(self):
        ''' Iterate over the chords '''
        return self.chords.__iter__()
    
    if __name__ == '__main__':
        print('Sample Chords usage')
        chords_file = "/Compile/dwbzen/resources/music/allChordFormulas.json"
        _chords = music.Chords(json_file_name = chords_file)
        _chord = _chords.chord['Ninth flat fifth']
        print(_chord.chord)
        print('Ninth flat fifth: {}'.format(_chord.notes))
        
        # get the notes for a different root
        _notes = _chord.scale.notes(root='A', accidental_preference='mixed')
        print(_notes)
        
        

    