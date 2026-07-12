# ------------------------------------------------------------------------------
# Name:          scale.py
# Purpose:       Encapsulate a musical scale.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2022 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
import json
from typing import List

def find_note_in_scale(note):
    # returns the index of note in one of the CHROMATIC scales or -1 if not there
    _note = note.upper()
    _index = -1
    if(Scale.has_octave(note)):
        _note = _note[0:len(note)-1]
    if _note in Scale.CHROMATIC_SHARP_PITCHES:
        _index = Scale.CHROMATIC_SHARP_PITCHES.index(_note)
    elif _note in Scale.CHROMATIC_FLAT_PITCHES:
        _index = Scale.CHROMATIC_SHARP_PITCHES.index(_note)
    return _index

class Scale:
    """
    TODO - class needs to be cleaned up
    
    A single Scale as a dictionary with keys:
    name - primary lookup key
    alternateNames - list of AKAs
    groups - list of group names the scale is a member of
    formula - a list of integer intervals that define the scale. 
        Given a root note, the first interval is number of half steps to raise that note to obtain the next note.
        Subsequent notes are obtained by raising the current note that number of half steps.
        For example, with a root note 'C', and the formula [2, 2, 1, 2, 2, 2, 1], the resulting notes are:
        C (+2) D (+2) E (+1) F (+2) G (+2) A (+2) B (+1) C. The number of notes produced by a give formula
        is len(formula)+1. The sum of the intervals in a given formula MUST equal 12.
    size - number of notes in the scale excluding the final note, which is an octave above the root.
        So the size of diatonic scales (major, harmonic minor, etc.) is 7.
    """
    
    # chromatic pitches given over a 2-octave range
    SHARP_PITCHES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    FLAT_PITCHES =  ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
    MIXED_PITCHES = ['C','C#','D','Eb','E','F','F#','G','G#','A','Bb','B']
    CHROMATIC_SHARP_PITCHES = SHARP_PITCHES + SHARP_PITCHES
    CHROMATIC_FLAT_PITCHES = FLAT_PITCHES + FLAT_PITCHES
    CHROMATIC_MIXED_PITCHES = MIXED_PITCHES + MIXED_PITCHES

    @classmethod
    def has_octave(cls, note):
        _result = len(note) > 0 and note[len(note)-1].isdigit()
        return _result

    @classmethod
    def get_octave(cls, note):
        if(Scale.has_octave(note)):
            return  note[len(note)-1]
        else:
            return None

    @classmethod
    def get_pitch(cls, note):
        _pitch = note
        if(Scale.has_octave(note)):
            _pitch = _pitch[0:len(note)-1]
        return _pitch
        
    def __init__(self, scale_data:dict={}):
        '''
        Create a Scale from a dictionary
        Argument:
            scale_data a dict representing a single scale having the keys described above
                for example: { "name" : "Major" , "groups" : [ "major", "diatonic", "common"] , "formula" : [2,2,1,2,2,2,1] , "size" : 7}
                Default is an empty dict. Use the setter functions to add values to individual fields.
        '''
        # print("raw data: {}".format(raw_data))
        self.scale_data = scale_data
        if len(scale_data) > 0:
            self.scale = scale_data
            self._name = self.scale.get('name', "MY_SCALE")
            self._formula = self.scale.get('formula', [])
            self._size = self.scale.get("size", 0)
            self._groups = self.scale.get("groups", [])
            self._alternate_names = self.scale.get("alternateNames", [])
        else:
            scale_data = {}

        self._chromatic_scale = []

    def __iter__(self):
        """ Iterate over the notes in the scale """
        return self.scale.__iter__()
    
    @property
    def name(self)->str:
        return self._name
    
    @name.setter
    def name(self, newname):
        self.name = newname
        
    @property
    def formula(self)->List[int]:
        return self._formula
    
    @formula.setter
    def formula(self, newformula):
        self.formula = newformula
        self.size = len(newformula)

    def pitches(self, root='C4', accidental_preference=None):
        """
        Creates and returns the list of notes for this scale starting with the root provided. the default root is 'C4' (middle C).
        If the root provided lacks an octave, 4 is assumed.
        By convention, pitches are expressed in scientific music notation which includes an octave designation starting at 0
        For example, the range of a Piano is A0 to C8.
        Octaves are from C to B, so the pitch following B4 is C5.
        In general the accidental (# or b) used is determined first by the root note. If the root doesn't have an accidental,
        the accidental_preference is used. If a preference is not provided a # is the default.
        Preferences: 'sharp', '#', 'flat', 'b', 'mixed', '#b'
        """
        _ap = self.get_accidental_preference(root, accidental_preference)
        _p = Scale.get_pitch(root)
        _notes = self.notes(_p, accidental_preference)
        if not Scale.has_octave(root):
            return _notes
        #
        # add the octave to each note
        #
        _octave = int(Scale.get_octave(root))
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


    def notes(self, root='C', accidental_preference=None):
        """
        Creates and returns the list of notes for this scale starting with the root note provided. the default root is 'C'. 
        By convention, notes do not include an octave designation.
        """
        _root = root
        if(Scale.has_octave(root)):
            _root = root[0:len(root)-2]
        _notes = [_root]
        _ap = self.get_accidental_preference(root, accidental_preference)
        _ind = self._chromatic_scale.index(_root)
        for i in self.formula:
            _ind += i
            _notes.append(self._chromatic_scale[_ind])
        return _notes
    
    def get_accidental_preference(self, root, accidental_preference):
        _ap = '#'
        if accidental_preference is None:
            if('#' in root):
                _ap = '#'
                self._chromatic_scale=Scale.CHROMATIC_SHARP_PITCHES
            elif('b' in root):
                _ap = 'b'
                self._chromatic_scale=Scale.CHROMATIC_FLAT_PITCHES
            else:
                _ap = '#b'
                self._chromatic_scale=Scale.CHROMATIC_MIXED_PITCHES
        else:
            if('#' == accidental_preference or 'sharp' == accidental_preference):
                _ap = '#'
                self._chromatic_scale=Scale.CHROMATIC_SHARP_PITCHES
            elif('b' == accidental_preference or 'flat' == accidental_preference):
                _ap = 'b'
                self._chromatic_scale=Scale.CHROMATIC_FLAT_PITCHES
            elif('#b' == accidental_preference or 'mixed' == accidental_preference):
                _ap = '#b'
                self._chromatic_scale=Scale.CHROMATIC_MIXED_PITCHES
            else:
                _ap = '#b'
                self._chromatic_scale=Scale.CHROMATIC_MIXED_PITCHES
        return _ap
    
    def __str__(self):
        return str(self.notes(root="C", accidental_preference='mixed'))
    
    def __repr__(self):
        return str(self.scale)
    
    def to_string(self, root:str)->str:
        return str(self.notes(root, accidental_preference='mixed'))
    
    def to_JSON(self)->dict:
        return self.scale_data

if __name__ == '__main__':
    print(Scale.__doc__)

        
        
        