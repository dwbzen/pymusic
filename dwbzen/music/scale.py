# -*- coding: utf-8 -*-
'''
Created on Feb 22, 2021

@author: don_bacon
'''
import json
import music
    
def has_octave(note):
    _result = len(note) > 0 and note[len(note)-1].isdigit()
    return _result

def get_octave(note):
    if(has_octave(note)):
        return  note[len(note)-1]
    else:
        return None

def get_pitch(note):
    _pitch = note
    if(has_octave(note)):
        _pitch = _pitch[0:len(note)-1]
    return _pitch
    
def find_note_in_scale(note):
    # returns the index of note in one of the CHROMATIC scales or -1 if not there
    _note = note.upper()
    _index = -1
    if(has_octave(note)):
        _note = _note[0:len(note)-1]
    if _note in Scale.CHROMATIC_SHARP_PITCHES:
        _index = Scale.CHROMATIC_SHARP_PITCHES.index(_note)
    elif _note in Scale.CHROMATIC_FLAT_PITCHES:
        _index = Scale.CHROMATIC_SHARP_PITCHES.index(_note)
    return _index

class Scale:
    CHROMATIC_SHARP_PITCHES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    CHROMATIC_FLAT_PITCHES =  ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
    CHROMATIC_MIXED_PITCHES = ['C','C#','D','Eb','E','F','F#','G','G#','A','Bb','B']
    
    '''
    A single Scale as a dictionary with keys:
    name - primary lookup key
    alternateNames - list of AKAs
    groups - list of group names the scale is a member of
    formula - a list of integer intervals that define the scale
    size - number of notes in the scale
    '''
        
    def __init__(self, raw_data={}):
        '''
        Constructor
        '''
        # print("raw data: {}".format(raw_data))
        if(type(raw_data) is dict):
            self.scale = raw_data
        else:
            self.scale = json.loads(raw_data)
            
        self.name = self.scale['name']
        self.formula = self.scale['formula']
        Scale.chromatic_sharp_pitches2 = Scale.CHROMATIC_SHARP_PITCHES.copy()
        Scale.chromatic_flat_pitches2 = Scale.CHROMATIC_FLAT_PITCHES.copy()
        Scale.chromatic_mixed_pitches2 = Scale.CHROMATIC_MIXED_PITCHES.copy()
        Scale.chromatic_sharp_pitches2 *=2  # two octaves
        Scale.chromatic_flat_pitches2 *=2    # two octaves
        Scale.chromatic_mixed_pitches2 *=2   # two octaves
        self._chromatic_scale = []

    '''
    Creates and returns the list of notes for this scale starting with the root provided. the default root is 'C4' (middle C).
    If the root provided lacks an octave, 4 is assumed.
    By convention, pitches are expressed in scientific music notation which includes an octave designation starting at 0
    For example, the range of a Piano is A0 to C8.
    Octaves are from C to B, so the pitch following B4 is C5.
    In general the accidental (# or b) used is determined first by the root note. If the root doesn't have an accidental,
    the accidental_preference is used. If a preference is not provided a # is the default.
    Preferences: 'sharp', '#', 'flat', 'b', 'mixed', '#b'
    '''
    def pitches(self, root='C4', accidental_preference=None):

        _ap = self.get_accidental_preference(root, accidental_preference)
        _p = get_pitch(root)
        _notes = self.notes(_p, accidental_preference)
        if not has_octave(root):
            return _notes
        #
        # add the octave to each note
        #
        _octave = int(get_octave(root))
        _ind = self._chromatic_scale.index(_p)
        _pitches = []
        i = 0
        next_octave = True
        for note in _notes:
            if(_ind > 11 and next_octave):
                _octave = _octave + 1
                next_octave = False
            _pitches.append('{}{}'.format(note,_octave))
            if(i < len(self.formula)):
                _ind = _ind + self.formula[i]
            i = i + 1
        return _pitches

    '''
    Creates and returns the list of notes for this scale starting with the root note provided. the default root is 'C'. 
    By convention, notes do not include an octave designation.
    '''
    def notes(self, root = 'C', accidental_preference=None):
        _root = root
        if(has_octave(root)):
            _root = root[0:len(root)-2]
        _notes = [_root]
        _ap = self.get_accidental_preference(root, accidental_preference)
        _ind = self._chromatic_scale.index(_root)
        for i in self.scale['formula']:
            _ind += i
            _notes.append(self._chromatic_scale[_ind])
        return _notes
    
    def get_accidental_preference(self, root, accidental_preference):
        _ap = '#'
        if accidental_preference is None:
            if('#' in root):
                _ap = '#'
                self._chromatic_scale=Scale.chromatic_sharp_pitches2
            elif('b' in root):
                _ap = 'b'
                self._chromatic_scale=Scale.chromatic_flat_pitches2
            else:
                _ap = '#b'
                self._chromatic_scale=Scale.chromatic_mixed_pitches2
        else:
            if('#' == accidental_preference or 'sharp' == accidental_preference):
                _ap = '#'
                self._chromatic_scale=Scale.chromatic_sharp_pitches2
            elif('b' == accidental_preference or 'flat' == accidental_preference):
                _ap = 'b'
                self._chromatic_scale=Scale.chromatic_flat_pitches2
            elif('#b' == accidental_preference or 'mixed' == accidental_preference):
                _ap = '#b'
                self._chromatic_scale=Scale.chromatic_mixed_pitches2
            else:
                _ap = '#b'
                self._chromatic_scale=Scale.chromatic_mixed_pitches2
        return _ap


    if __name__ == '__main__':
        print('Sample Scale usage')
        scales_file = "../../resources/common_scaleFormulas.json"
        _scales = music.Scales(json_file_name=scales_file)
        _scale = _scales.scale['Dorian b2']
        print(type(_scale))
        print("Dorian b2: {}".format(_scale.scale))
        print('formula: {}'.format(_scale.formula))
        _notes = _scale.notes(root='A', accidental_preference='mixed')
        print(_notes)
        
        _scale = _scales.scale['Mixolydian b5']
        print("Mixolydian b5: {}".format(_scale.scale))
        print('formula: {}'.format(_scale.formula))
        _notes = _scale.notes(root='B', accidental_preference='#')
        print(_notes)
        _pitches = _scale.pitches(root='B3')
        print(_pitches)
        
        
        