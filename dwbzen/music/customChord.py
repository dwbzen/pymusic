'''
Created on Oct 8, 2026

@author: don_bacon
'''

from music.chord import Chord, ChordPosition
from music.musicUtils import MusicUtils
from music.key import Key
from typing import List
import argparse

class CustomChord(Chord):
    """ A chord based on a custom formula or intervals
    """

    def __init__(self, name:str="MyChord", formula:List[int]=None, interval_names:List[str]=None, symbol:str="cus", root_pitch="C"):
        """
        Not finding what you need in common_chordFormulas.json?
        No problem - create your own custom chord from a formula or list of named intervals.
        Arguments:
            name - the user-defined name for this chord. If not specified the default name is "MyChord"
            formula - a list of ints > 0. Default is None.
            interval_names - a list of standard interval names (str). Default is None
            symbol - a user-defined symbol for this chord. Default is "cus" for custom
            root_pitch - the chord root, default is "C"
        Raises:
            TypeError if both formula and interval_names arguments are None.
            
        If both are not None, they should resolve to the same chord
        Note that the Key defaults to C-Major. It can be set with the key property setter.
        """
        if formula is None and interval_names is None:
            raise TypeError("At least one of formula, interval_names must not be None")
        
        formula = formula if formula is not None else MusicUtils.intervalNames_to_intervalSizes(interval_names)
        names:List[str] = interval_names if interval_names is not None else MusicUtils.intervalSizes_to_intervalNames(formula)
        fsize = len(formula)
        formulaNumber = MusicUtils.get_formulaNumber(formula)
        chord_data = {"name":name, "symbols":[symbol], "groups":["custom"], "formula":formula, 
                      "intervals":names, "size":fsize, "chordSize":fsize+1, "formulaNumber":formulaNumber}
        super().__init__(chord_data, root_pitch=root_pitch, position=ChordPosition.EXTENDED)
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Chords", description="Create a custom chord")
    parser.add_argument("--formula", "-F", help="Chord formula as a comma-separated list", type=str, default=None)
    parser.add_argument("--intervals", help="Comma-separated list of interval names", type=str, default=None)
    parser.add_argument("--name", help="Chord name", type=str, default=None)
    parser.add_argument("--symbol", "-S", help="User defined symbol string", type=str, default=None)
    parser.add_argument( "--root", "-R",help="Root pitch, default is 'C'. May also include an octave as in 'C4'", type=str, default="C")
    args = parser.parse_args()
    if args.formula is not None:
        fs = args.formula.split(",")
        formula = [int(x) for x in fs]
    else:
        formula = None
    interval_names = args.intervals.split(",") if args.intervals is not None else None
    custom_chord = CustomChord(name=args.name, formula=formula, interval_names=interval_names, symbol=args.symbol, 
                               root_pitch=args.root)
    
    custom_chord.show("musicxml", root=args.root, note_duration="whole")
    
    