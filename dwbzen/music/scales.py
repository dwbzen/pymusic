# ------------------------------------------------------------------------------
# Name:          scales.py
# Purpose:       Encapsulate music scales.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
import music
import argparse
import json
import pandas as pd


class Scales(object):
    """Scale formulas for common scales
    
    """
    scales_file = "/common_scaleFormulas.json"
    
    pitches_flats =  ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C' ]
    pitches_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C' ]
    pitches_mixed =  ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B', 'C' ]
    
    def __init__(self, verbose=0, resource_folder ="/Compile/dwbzen/resources/music"):

        self.scales = {}
        self.scale = {}
        self.data = {}
        self.scale_names = []
        self.resource_folder = resource_folder
        self.scales_file = resource_folder + Scales.scales_file
        self.verbose = verbose

        with open(self.scales_file, "r") as read_file:
            self.data = json.load(read_file)

        self.create_dataFrame()
        self.get_scales_data()
        
    def format_cols(self, formula, fnumber):
        return '{}:{}'.format(formula,fnumber)
    
    def get_pitch_set(self, formula):
        """
        Creates a List of relative pitch indexes, and a list of pitches for a given formula
        Each element is the number of steps from the root of 'C'.
        For example given the scale formula  [1, 2, 1, 2, 1, 2, 2, 1] (name == 'Shostakovich respelled all sharp')
        the resulting pitch set is [0, 1, 3, 4, 6, 7, 9, 11, 12] 
        If the root Pitch is C, the corresponding pitches are ['C#', 'Eb', 'E', 'F#', 'G', 'A', 'B', 'C']
        """
        ps = [0]
        pitches = ['C']
        for i in range(0,len(formula)):
            ind = formula[i] + ps[i]
            ps.append(ind)
            pitches.append(self.pitches_mixed[ind])
        return (ps, pitches)
    
    def formula_number(self, formula):
        """
        The formula number of a chord/scale formula is an integer unique to that formula
        It is created from the pitch_set of the formula by successive left shifts
        """
        fnum = 0
        (pitch_set) = self.get_pitch_set(formula)
        for i in pitch_set[0]:
            shiftamt = i
            if i >= 12:
                shiftamt = 12-1
            fnum = fnum + (1 << shiftamt)
        return fnum

    def create_dataFrame(self):
        self.column_names = ['name', 'alternateNames', 'groups', 'formula', 'size']
        self.scales_df = pd.DataFrame(data=self.data['scales'], columns=self.column_names)
        #
        # alternateNames need to be a list so if a scale doesn't have any alternateNames
        # set it to a single item list consisting of the name
        #
        missing_series = self.scales_df[self.scales_df['alternateNames'].isnull()]['name'].apply(lambda x:[x])
        self.scales_df['alternateNames'].fillna(missing_series, inplace=True)
        
        # add the formula number for each scale
        self.scales_df['formula_number'] =  self.scales_df['formula'].apply(self.formula_number)
        
        # create a formula_str column which combines the formula number and formula into a single string
        self.scales_df['formula_str'] = self.scales_df[['formula_number','formula']].apply(lambda df: self.format_cols( df['formula_number'], df['formula']),axis=1)

        # self.scales_df.set_index('name')
    

    def get_scales_data(self):
        self.scales = self.data['scales']
        for s in self.scales:
            self.scale_names.append(s['name'])
            self.scale[s['name']] = music.Scale(s)

    def __iter__(self):
        """ Iterate over the scales
        
        """
        return self.scales.__iter__()
        
if __name__ == '__main__':
    _scales = Scales()
    scales_df = _scales.scales_df
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--name", help="Scale name", type=str, default=None)
    parser.add_argument("-g", "--group", help="Group name", type=str, default=None)
    args = parser.parse_args()
    
    if args.name is not None:
        _scale = _scales.scale[args.name]
        print('{} formula: {}'.format(args.name, _scale.formula))
        _notes = _scale.notes(root='A', accidental_preference='mixed')
        print('{} notes: {}'.format(args.name, _notes))
        print(str(_scale))
    if args.group is not None:
        group_scales = scales_df[scales_df['groups'].apply(lambda x:args.group in x)]
        print(group_scales)
    