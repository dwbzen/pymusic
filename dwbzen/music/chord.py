'''
Created on Mar 3, 2021

@author: don_bacon
'''
import json
from music.scale import Scale
from music.key import Key
from music21 import scale,chord,note, metadata
from music21 import stream, interval
import music21
from typing import List

class Chord(object):
    
    C_MAJOR_KEY = { "name" : "C-Major", "alternate_name" : "C major", "mode" : "Major", "accidental" : "mixed", "signature" : 0, "relativeKey" : "A-Minor" }

    def __init__(self, chord_data:dict, key:Key=None):
        """
        Create a Chord instance from a dictionary, for example: 
        {"name":"Major seventh",  "symbols":["maj7","M7"],   "groups":["seventh"], 
           "formula":[4,3,4],     "intervals":["M3","m3","M3"], "size":3, 
           "chordSize":4,         "formulaNumber":2193,     "spelling":"C E G B" },
        Arguments:
            chord_data - a dictionary with the above structure.
            key - an optional Key instance. This gives the tonic (root) note of the chord if provided,
                  else the Key is set to C-Major,  root is 'C'.
        """
        print(f"chord data: {chord_data}")
        self.chord_data = chord_data
        self.name = self.chord_data['name']
        self.formula = self.chord_data['formula']
        self.intervals = self.chord_data['intervals']
        self._notes = self.chord_data['spelling'].split()
        self.symbols = self.chord_data['symbols']
        self.size = len(self.formula)
        self._key = Key(Chord.C_MAJOR_KEY) if key is None else key
        self._music21Key = music21.key.KeySignature(0)      # key.KeySignature
        self._music21Chord = None    # chord.Chord
    
    @property
    def notes(self)->List[str]:
        return self._notes
    
    def get_music21_key(self, transpose_interval:interval.Interval|None=None)->music21.key.Key:
        """ 
        """
        if self._music21Key is None:
            accidental = -1 if self.key.accidental == "flat" else 1
            semitones = transpose_interval.semitones if transpose_interval is not None else 0
            signature = self.key.signature  * accidental  # number of sharps or flats, no need transpose the  key
            music21Key = music21.key.KeySignature(signature)
            self._music21Key = music21Key if semitones == 0 else music21Key.transpose(semitones)
        return self._music21Key
        
    def _create_music21_objects(self):
        self._music21Chord = chord.Chord(self.notes)
        
    
    def show(self, format_:str, root="C4", octaves=1, notes:List[str]=None, note_duration="quarter", 
             instrument_name="Piano", metronome_mark:(int,str)=(120,"quarter"), time_signature:str="4/4"):
        
        part_stream = stream.Stream()
        part_stream.insert(0, metadata.Metadata())
        part_stream.metadata.title = self.name
        part_stream.insert(self._music21Key)
        
        
