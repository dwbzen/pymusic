'''
Created on Sep 11, 2026

@author: don_bacon
'''

import json
from typing import List, Set
from music.chord import Chord
from common.environment import Environment
import pandas as pd

class ChordLibrary(object):
    """ Chord formulas """
    
    CHORDS_FILE = "allChordFormulas.json"

    def __init__(self, chords_filename:str=None):
        '''
        Constructor
        '''
        env = Environment.get_environment()
        resource_folder = env.get_resource_folder("music")
        self.chords_filename = ChordLibrary.CHORDS_FILE if chords_filename is None else chords_filename
        self.chords_file = f"{resource_folder}/{self.chords_filename}"
        with open(self.chords_file, "r") as read_file:
            chords_data = json.load(read_file)
        
        self._chordsLib = {}
        self._chordsData = chords_data["chordFormulas"]
        self._chordNames = []
        self._chords_df = None
        
        for chord in self._chordsData:
            name = chord["name"]
            self._chordNames.append(name)
            self._chordsLib[name] = chord
            self._chordsLib[name.lower()] = chord
            
        # extract and save all the group names
        self._groupNames = chords_data["groups"]
            
    
    def getChordDataFrame(self)->pd.DataFrame:
        for cdata in self._chordsData:
            self.chord[cdata['name']] = Chord(cdata)
        self._chords_df = pd.DataFrame(self.chords)
        return self._chords_df
    
    @property
    def chords_df(self):
        return self._chords_df

    @property
    def chordsLib(self)->dict:
        return self._chordsLib
    
    @property
    def chordNames(self)->List[str]:
        return self._chordNames
    
    @property
    def chordsData(self)->dict:
        return self._chordsData
    
    def __iter__(self):
        ''' Iterate over the chords '''
        return self._chords_df.__iter__()
    
def main():
    # from .chordLib import ChordLib
    print('Sample Chords usage')
    chordLibary = ChordLibrary()
    chord_data = chordLibary.chordsLib['Ninth flat fifth']
    print(chord_data)
    chord = Chord(chord_data)
    print(f"Ninth flat fifth: {chord.notes}")
    
    # get the notes for a different root
    #notes = chord.scale.notes(root='A', accidental_preference='mixed')
    #print(notes)
        
if __name__ == '__main__':
    main()