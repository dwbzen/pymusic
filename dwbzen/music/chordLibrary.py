'''
Created on Sep 11, 2026

@author: don_bacon
'''

import json, argparse
from typing import List, Dict
from music.chord import Chord
from music.key import Key
from music.chord import ChordPosition
from common.environment import Environment
import pandas as pd

class ChordLibrary(object):
    """ Chord formulas """
    
    CHORDS_FILE = "common_chordFormulas.json"

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
        
        # build a Dict[str, dict] that indexes the chords by symbol
        self._symbols = {}
        for chord in self._chordsData:
            cs = {x: chord for x in chord["symbols"]}
            self._symbols.update(cs)
    
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
    
    @property
    def symbols(self)->Dict[str,dict]:
        return self._symbols
    
    def getChord(self, name:str, position:ChordPosition=ChordPosition.EXTENDED, rootNote:str="C4", key:Key=None, inversion:int=0, doubleRoot=False)->Chord:
        chord_data = self.chordsLib[name]
        chord = Chord(chord_data, root_pitch=rootNote, key=key, position=position, inversion=inversion, doubleRoot=doubleRoot)
        return chord
    
    def getChordBySymbol(self, symbol:str, position:ChordPosition=ChordPosition.CLOSED, rootNote="C", key:Key=None)->Chord:
        chord_data = self._symbols.get(symbol, None)
        chord = Chord(chord_data, root_pitch=rootNote, key=key, position=position) if chord_data is not None else None
        return chord
    
    def __iter__(self):
        ''' Iterate over the chords '''
        return self._chords_df.__iter__()

    def toJson(self, indent:int=None, sort_keys=True)->str:
        js = json.dumps(self.chordsLib, indent=indent, sort_keys=sort_keys)
        return js
    
def main():

    description = "Create a library of Chords from a JSON chords file. Sample usage."
    parser = argparse.ArgumentParser(prog="ChordLibrary", description=description)
    parser.add_argument("filename", help="Chords JSON file", type=str, default=None)
    parser.add_argument("--name", "-N", help="Chord name", type=str, default="Major")
    parser.add_argument("--verbose", "-v", help="increase output verbosity", action="count", default=0)
    args = parser.parse_args()
    
    print(f"Chords JSON file: {args.filename}")
    chordslib = ChordLibrary(args.filename)
    if args.verbose > 1:
        print(f"chordsLib: {chordslib.toJson()}")
    if args.verbose > 0:
        print(f"chord names: {chordslib.chordNames}")
    
    chord_data = chordslib.chordsLib[args.name]
    print(f"{args.name} chord data: {chord_data}")
    chord = chordslib.getChord(args.name)
    print(f"{chord.root} {args.name} notes: {chord.notes}")
    
        
if __name__ == '__main__':
    main()