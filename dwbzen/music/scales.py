# ------------------------------------------------------------------------------
# Name:          scales.py
# Purpose:       Encapsulate music scales.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2022 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from music.scale import Scale
from music.scaleLib import ScaleLib
from music.keys import Keys
from music.key import  Key
import argparse
import json
import pandas as pd
import sys
from typing import List, Set

class Scales(object):
    """Scale formulas for common scales
    """
    SCALES_FILE = "common_scaleFormulas.json"
    
    def __init__(self, key:Key, scales_filename:str=None):
        
        # creates a dict with scale name and alternate name(s) adding lower case as keys
        self.scaleLib = ScaleLib(scales_filename)
        self.groupNames = self.scaleLib.groupNames
        self.scales_data = self.scaleLib.scalesData     # List[dict] from the scales JSON file
        
        self.scales_df = self.create_dataFrame()    # also sets self.scales attribute
        self.key_name = key.key_name

        
    def format_cols(self, formula:List[int], fnumber:int):
        return f"{formula}: {fnumber}"
    
    @staticmethod
    def formula_number(formula):
        """
        The formula number of a chord/scale formula is an integer unique to that formula
        It is created from the pitch_set of the formula by successive left shifts
        """
        fnum = 0
        ps = Scale.get_pitch_set(formula)
        pitch_set = ps["pitch_set"]
        for i in pitch_set:
            shiftamt = i
            if i >= 12:
                shiftamt = 12-1
            fnum = fnum + (1 << shiftamt)
        return fnum
    
    def get_scales_data(self)->dict:
        """ Returns a List[dict] where each dictionary is the scale data for a single named scale.
        """
        return self.scales_data
    
    def get_scale(self, name:str, key:Key, octaves=1, descending=False)->Scale:
        """ Get a Scale by name or alternameName.
            Returns a Scale object
        """
        _scale = self.scaleLib.getScaleData(name)
        if _scale is None:
            _scale = self.scaleLib.getScaleData(name.lower())
        scale = None if _scale is None else Scale( _scale, key, octaves=octaves, descending=descending)
        return scale
    
    def create_dataFrame(self)->pd.DataFrame:
        column_names = ['name', 'alternateNames', 'groups', 'formula', 'size']
        scales_df = pd.DataFrame(data=self.scales_data, columns=column_names)
        return scales_df
    
    def _get_all_group_names(self)->Set(str):
        return self.scaleLib.groupNames

    def __iter__(self):
        """ Iterate over the scales
        """
        return self.scales.__iter__()
        
if __name__ == '__main__':

    keys = Keys()
    key_names = keys.key_names
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", "-N", help="Scale name", type=str, default=None)
    parser.add_argument("--group","-G",  help="Group name", type=str, default=None)
    parser.add_argument( "--root", "-R",help="Root pitch, default is 'C'. May also include an octave as in 'D3'", type=str, default="C")
    parser.add_argument("--key", "-K", 
            help="Optional key signature, for example 'Eb-Major', default key signature is 'C-Major'. Used to determine accidentals in the scale and also the tonic note.",
            choices = key_names, type=str, default="C-Major")
    parser.add_argument("--octaves", "-O", 
            help="Octave range, default is 1 octave", type=int, choices=[1,2,3,4], default=1)
    parser.add_argument("--descending", "-D", 
            help="Show both ascending and descending versions of the scale over the specified octave range. Default is False",
            action="store_true", default=False)
    parser.add_argument("--dup", help="Duplicate the scale in a separate part, the number of octaves higher or lower as indicated",
            type=int, choices=list(range(-2, 2)), default=0 )
    parser.add_argument("--show", "-S", help="Display a scale in MuseScore, lilypond or as a list",  
            type=str, choices=["pitches", "notes", "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf"], default="notes")
    parser.add_argument("--duration", help="Duration of the notes. Default is 'quarter'", type=str, 
            choices=["whole","half","quarter","eighth","16th","32nd","64th"], default="quarter")
    parser.add_argument("--instrument", help="The instrument name, default is 'Piano'", type=str, default="Piano")
    args = parser.parse_args()
    
    key:Key = keys.key(args.key)
    scales = Scales(key)
    scales_df = scales.scales_df
    #print(scales_df)
    
    if args.name is not None:
        scale = scales.get_scale(args.name, key,  args.octaves, args.descending)
        if scale is None:
            print(f"The scale '{args.name}' not found", file=sys.stderr)
            sys.exit()
        
        print(f"{args.name} formula: {scale.formula}")
        ps = Scale.get_pitch_set(scale.formula, args.root)
        print(f"pitch set: {ps['pitch_set']}  notes: {ps['pitches']}")
        
        formula_number = scales.formula_number(scale.formula)
        bin_formula_number = f"{formula_number:12b}".strip()
        print(f"formula number: {formula_number}, '{bin_formula_number}'")
        print(f"Scale: {scale.to_string(args.root)}")
        
        pitches = scale.pitches(args.root, octaves=args.octaves)
        notes = scale.notes(args.root, num_octaves=args.octaves)
        if args.show == "pitches" or args.show == "musicxml":
            print(f"pitches: {pitches}")
            print(f"notes: {notes}")
        if args.show == "notes":
            print(f"notes: {notes}")
        else:
            scale.show(args.show, root=args.root, notes=notes, note_duration=args.duration, 
                       instrument_name=args.instrument, second_part_transpose=args.dup, metronome_mark=(100,"quarter"))
        
    if args.group is not None:
        group_scales = scales_df[scales_df['groups'].apply(lambda x:args.group in x)]
        print(f"scales in {args.group}:\n{group_scales}")
    