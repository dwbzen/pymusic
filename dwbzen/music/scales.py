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
from music.keys import Key
from common.environment import Environment
import argparse
import json
import pandas as pd
from typing import List
from itertools import accumulate
import operator

class Scales(object):
    """Scale formulas for common scales
    """
    SCALES_FILE = "common_scaleFormulas.json"
    
    def __init__(self, scalesfilename:str=None):
        env = Environment.get_environment()
        resource_folder = env.get_resource_folder()
        self.scales = {}
        self.scale = {}
        self.data = {}
        self.scale_names = []
        self.resource_folder = resource_folder
        self.scales_file_name = Scales.SCALES_FILE if scalesfilename is None else scalesfilename
        self.scales_file = f"{resource_folder}/music/{self.scales_file_name}"
        self.scales_df = self.create_dataFrame()    # also sets scales attribute
        
    def format_cols(self, formula:List[int], fnumber:int):
        return f"{formula}: {fnumber}"
    
    @staticmethod
    def get_pitch_set(formula:List[int], root_pitch:str="C", accidental:str=None, include_octave=False)->dict:
        """
        TODO - this should be in the Scale class.
        
        Creates a List of relative pitch indexes, and a list of pitches for a given formula
        Each element is the number of steps from the root of 'C'.
        For example given the scale formula  [1, 2, 1, 2, 1, 2, 2, 1] (name == 'Shostakovich respelled all sharp')
        the resulting pitch set is [0, 1, 3, 4, 6, 7, 9, 11, 12] 
        If the root Pitch is C, the corresponding pitches are ['C', 'C#', 'Eb', 'E', 'F#', 'G', 'A', 'B']
        Arguments:
            formula - the scale formula as a List[int].
            root_pitch - the starting note to use
            accidental is the accidental to use when creating pitches. If None (the default) the cromatic
                pitch set to use is based on the root_pitch. Otherwise specify "#' or "b".
            include_octave - if True, add the root_pitch at the end, representing a full octave.
                default is False.
        Returns a dict with keys "pitch_set" (the index of cromatic notes in the scale), and "pitches"
        """
        pitch_set = list(accumulate(formula, operator.add, initial=0)) if include_octave else list(accumulate(formula, operator.add, initial=0))[:-1]

        if "b" in  root_pitch or accidental == "b":
            ind = Scale.CHROMATIC_FLAT_PITCHES.index(root_pitch)
            pitches = [Scale.CHROMATIC_FLAT_PITCHES[x+ind] for x in pitch_set]
        elif "#" in root_pitch or accidental == "#" or root_pitch[0] in "GDAEB":    # there's # in the root_pitch or it's the root of a sharp key
            ind = Scale.CHROMATIC_SHARP_PITCHES.index(root_pitch.upper())
            pitches = [Scale.CHROMATIC_SHARP_PITCHES[x+ind] for x in pitch_set]
        else:
            ind = Scale.CHROMATIC_FLAT_PITCHES.index(root_pitch)
            pitches = [Scale.CHROMATIC_FLAT_PITCHES[x+ind] for x in pitch_set]
        return {"pitch_set" : pitch_set, "pitches" : pitches}
    
    @staticmethod
    def formula_number(formula):
        """
        The formula number of a chord/scale formula is an integer unique to that formula
        It is created from the pitch_set of the formula by successive left shifts
        """
        fnum = 0
        ps = Scales.get_pitch_set(formula)
        pitch_set = ps["pitch_set"]
        for i in pitch_set:
            shiftamt = i
            if i >= 12:
                shiftamt = 12-1
            fnum = fnum + (1 << shiftamt)
        return fnum
    
    def get_scale(self, name:str)->Scale:
        """Get a Scale by name or alternameName   """
        # TODO could speed this up by creating a new dict with scale name as the key
        scale = None
        _name = name.lower()
        for s in self.scales:
            if s["name"].lower() == _name:
                scale = Scale(s)
                break
            else:
                if "alternateNames" in s:
                    for alt_name in s["alternateNames"]:
                        if alt_name.lower() ==_name:
                            scale = Scale(s)
                            break
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

    def __iter__(self):
        """ Iterate over the scales
        """
        return self.scales.__iter__()
        
if __name__ == '__main__':
    scales = Scales()
    scales_df = scales.scales_df
    #print(scales_df)
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--name", help="Scale name", type=str, default=None)
    parser.add_argument("-g", "--group", help="Group name", type=str, default=None)
    parser.add_argument("-r", "--root", help="Root pitch, default is 'C'", type=str, default="C")
    args = parser.parse_args()
    
    if args.name is not None:
        scale = scales.get_scale(args.name)
        print(f"{args.name} formula: {scale.formula}")
        ps = Scales.get_pitch_set(scale.formula, args.root)
        print(f"pitch set: {ps['pitch_set']}  pitches: {ps['pitches']}")
        formula_number = scales.formula_number(scale.formula)
        bfnumber = f"{formula_number:12b}".strip()
        print(f"formula number: {formula_number}, {bfnumber}")
        print(f"Scale: {scale.to_string(args.root)}")
        
    if args.group is not None:
        group_scales = scales_df[scales_df['groups'].apply(lambda x:args.group in x)]
        print(group_scales)
    