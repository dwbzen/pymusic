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
from music.keys import Keys
from music.key import  Key
from music21 import stream, note
from common.environment import Environment
import argparse
import json
import pandas as pd
import sys
from typing import List
from itertools import accumulate
import operator

class Scales(object):
    """Scale formulas for common scales
    """
    SCALES_FILE = "common_scaleFormulas.json"
    
    def __init__(self, key:Key, scales_filename:str=None):
        
        env = Environment.get_environment()
        resource_folder = env.get_resource_folder("music")
        self.scales = None
        self.scale = {}
        self.data = {}
        self.scale_names = []
        self.resource_folder = resource_folder
        self.scales_file_name = Scales.SCALES_FILE if scales_filename is None else scales_filename
        self.scales_file = f"{resource_folder}/{self.scales_file_name}"
        self.scales_df = self.create_dataFrame()    # also sets self.scales attribute
        self.group_names = self._get_all_group_names()
        self.key_name = key.key_name

        # create a dict with scale name and alternate name(s) adding lower case as keys
        self.scales_dict = {}
        for scale in self.scales:
            name = scale["name"]
            self.scales_dict[name] = scale
            self.scales_dict[name.lower()] = scale
            alt_names = scale.get("alternateNames", [])
            for alt_name in alt_names:
                self.scales_dict[alt_name] = scale
                self.scales_dict[alt_name.lower()] = scale
            
        # print(sorted(self.group_names))
        
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
    
    def get_scale(self, name:str, key:Key, octaves=1, descending=False)->Scale:
        """ Get a Scale by name or alternameName.
            Returns a Scale object
        """
        name = name
        _scale = self.scales_dict.get(name, None)
        if _scale is None:
            _scale = self.scales_dict.get(name.lower(), None)
        scale = None if _scale is None else Scale( _scale, key, octaves, descending)
        return scale
    
    def create_dataFrame(self)->pd.DataFrame:
        scales = self.get_scales_data()
        column_names = ['name', 'alternateNames', 'groups', 'formula', 'size']
        scales_df = pd.DataFrame(data=scales["scales"], columns=column_names)
        self.scales = scales["scales"]
        return scales_df

    def get_scales_data(self)->dict:
        with open(self.scales_file, "r") as read_file:
            scales_data = json.load(read_file)
            for s in scales_data["scales"]:
                if "alternateNames" not in s:
                    val = s["name"].lower()
                    s["alternateNames"] = [val]
                    # print(s)
        return scales_data
    
    def _get_all_group_names(self):
        group_names = set()
        for scale in self.scales:
            for group in scale["groups"]:
                group_names.add(group)
        return group_names

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
            help="Optional key name, for example 'Eb-Major', default key is 'C-Major'. Used to determine accidentals in the scale and also the root note.",
            choices = key_names, type=str, default="C-Major")
    parser.add_argument("--octaves", "-O", 
            help="Octave range, default is 1 octave", type=int, choices=[1,2,3,4], default=1)
    parser.add_argument("--descending", "-D", 
            help="Show both ascending and descending versions of the scale over the specified octave range. Default is False",
            action="store_true", default=False)
    parser.add_argument("--dup", help="Duplicate the scale in a separate part, the number of octaves higher or lower as indicated",
            type=int, choices=list(range(-2, 3)), default=0 )
    parser.add_argument("--show", "-S", help="Display a scale in MuseScore, lilypond or as a list",  
            type=str, choices=["musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf", "pitches", "notes"], default=False)
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
        
        pitches = scale.pitches(args.root)
        notes = scale.notes(args.root)
        if args.show == "pitches" or args.show == "musicxml":
            print(f"pitches: {pitches}")
        if args.show == "notes":
            print(f"notes: {notes}")
        else:
            scale.show(args.show, notes=notes)
        
    if args.group is not None:
        group_scales = scales_df[scales_df['groups'].apply(lambda x:args.group in x)]
        print(f"scales in {args.group}:\n{group_scales}")
    