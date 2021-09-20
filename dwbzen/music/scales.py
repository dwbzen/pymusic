'''
Created on Feb 22, 2021

@author: don_bacon
'''
import music
import json
import pandas as pd


class Scales:
    '''
    Scale formulas for common scales
    Can also use pandas as pd to read in the JSON, for example:
    filename = "C:\\data\\music\\common_scaleFormulas.json"
    scales_df =  pd.read_json(filename, orient='columns')
    scale = scales_df.iloc[0]
    scale_dict = dict(scale)
    formula = scale_dict['scales']['formula']   # returns the formula as an integer list
    
    '''
    scales_file = "../../resources/common_scaleFormulas.json"
    
    pitches_flats =  ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C' ]
    pitches_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C' ]
    pitches_mixed =  ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B', 'C' ]
    
    def mklist(self, x):
        '''
        creates and returns a list consisting of the single object passed
        '''
        lst = []
        lst.append(x)
        return lst
    
    def format_cols(self, formula, fnumber):
        return '{}:{}'.format(formula,fnumber)
    
    def get_pitch_set(self, formula):
        '''
        Creates a List of relative pitch indexes, and a list of pitches for a given formula
        Each element is the number of steps from the root of 'C'.
        For example given the scale formula  [1, 2, 1, 2, 1, 2, 2, 1] (name == 'Shostakovich respelled all sharp')
        the resulting pitch set is [0, 1, 3, 4, 6, 7, 9, 11, 12] 
        If the root Pitch is C, the corresponding pitches are ['C#', 'Eb', 'E', 'F#', 'G', 'A', 'B', 'C']
         '''
        ps = [0]
        pitches = ['C']
        for i in range(0,len(formula)):
            ind = formula[i] + ps[i]
            ps.append(ind)
            pitches.append(self.pitches_mixed[ind])
        return (ps, pitches)
    
    def formula_number(self, formula):
        '''
        The formula number of a chord/scale formula is an integer unique to that formula
        It is created from the pitch_set of the formula by successive left shifts
        '''
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
        missing_series = self.scales_df[self.scales_df['alternateNames'].isnull()]['name'].apply(lambda x:self.mklist(x))
        self.scales_df['alternateNames'].fillna(missing_series, inplace=True)
        # add the formula number for each scale
        self.scales_df['formula_number'] =  self.scales_df['formula'].apply(self.formula_number)
        
        # create a formula_str column which combines the formula number and formula into a single string
        self.scales_df['formula_str'] = self.scales_df[['formula_number','formula']].apply(lambda df: self.format_cols( df['formula_number'], df['formula']),axis=1)

        # self.scales_df.set_index('name')
    
    def __init__(self, raw_data={}, json_file_name=''):
        '''
        Constructor
        '''
        self.scales = {}
        self.scale = {}
        self.scales_file = ''
        self.data = {}
        self.scale_names = []
        if (len(json_file_name) >0):
            self.scales_file = json_file_name
            with open(self.scales_file, "r") as read_file:
                self.data = json.load(read_file)
        else:
            self.data = raw_data
        self.create_dataFrame()
        self._get_scales_data()
        
    def _get_scales_data(self):
        self.scales = self.data['scales']
        for s in self.scales:
            self.scale_names.append(s['name'])
            self.scale[s['name']] = music.Scale(s)

    def __iter__(self):
        ''' Iterate over the scales '''
        return self.scales.__iter__()
        
    if __name__ == '__main__':
        _scales = music.Scales(json_file_name=scales_file)
        scales_df = _scales.scales_df
        scales_df_blues = scales_df[scales_df['groups'].apply(lambda x:'blues' in x)]

        