'''
Created on Sep 22, 2026

@author: don_bacon
'''
from functools import cached_property
from typing import Dict, List
from music.musicUtils import MusicUtils
from music21 import pitch

class Notes(object):
    
    # chromatic pitches given over a 4-octave range
    SHARP_PITCHES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    FLAT_PITCHES =  ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
    MIXED_PITCHES = ['C','C#','D','Eb','E','F','F#','G','G#','A','Bb','B']
    CHROMATIC_SHARP_PITCHES = 4 * SHARP_PITCHES
    CHROMATIC_FLAT_PITCHES =  4 * FLAT_PITCHES
    CHROMATIC_MIXED_PITCHES = 4 * MIXED_PITCHES
    NATURAL_PITCHES = ["C","D","E","F","G","A","B"]
    
    # translation table of note type names to a numerical value
    NOTE_VALUES = {"whole":1, "half":2, "quarter":4, "eighth":8, "16th":16, "32nd":32}
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"
    DOUBLE_FLAT_M21 = "--"
    
    def __init__(self, start_octave=0, num_octaves=10)->None:
        self._num_octaves = num_octaves
        self._start_octave = start_octave
    

    def get_chromatic_flat_pitches(self)->List[str]:
        return Notes.CHROMATIC_FLAT_PITCHES

    def get_chromatic_sharp_pitches(self)->List[str]:
        return Notes.CHROMATIC_SHARP_PITCHES

    def get_chromatic_mixed_pitches(self)->List[str]:
        return Notes.CHROMATIC_MIXED_PITCHES
    
    def get_note_values(self)->Dict[str,int]:
        return Notes.NOTE_VALUES
    
    @property
    def num_octaves(self)->int:
        return self._num_octaves
    
    @num_octaves.setter
    def num_octaves(self,n:int):
        self._num_octaves = n
    
    @property
    def start_octave(self)->int:
        return self._start_octave
    
    @cached_property
    def chromatic_pitches(self)->Dict[str,List[str]]:
        """ Returns a list of chromatic pitches in ascending order over the number of octaves indicated.
            Arguments: 
                num_octaves - the octave range, default value is 2.
                start_octave - optional argument to produce notes in scientific notation (pitch+octave as in C4).
                    Default value is -1, an invalid octave designation.
        """
        cpf = self.num_octaves * Notes.FLAT_PITCHES       # 12 pitches x #octaves
        cps = self.num_octaves * Notes.SHARP_PITCHES
        cpm = self.num_octaves * Notes.MIXED_PITCHES
        chromatic_pitches = {"flat":cpf, "sharp":cps, "mixed":cpm}
        return chromatic_pitches
    
    @cached_property
    def chromatic_notes(self)->Dict[str,List[str]]:
        cpf = []
        cps = []
        cpm = []
        for octave in range(self.start_octave, self.start_octave+self.num_octaves):
            for pitch in Notes.FLAT_PITCHES:
                cpf.append(f"{pitch}{octave}")
            for pitch in Notes.SHARP_PITCHES:
                cps.append(f"{pitch}{octave}")
            for pitch in Notes.MIXED_PITCHES:
                cpm.append(f"{pitch}{octave}")
        chromatic_notes = {"flat":cpf, "sharp":cps, "mixed":cpm}
        return chromatic_notes
    
    def get_note_number(self, *notes)->Dict[str,int]:
        note_numbers = {}
        cnotes = self.chromatic_notes
        for anote in notes:
            if Notes.DOUBLE_SHARP in anote:
                p = pitch.Pitch(anote)
                n = p.getEnharmonic().nameWithOctave
                note_ = MusicUtils.get_note(n)
            elif Notes.DOUBLE_FLAT in anote:
                p = pitch.Pitch(anote.replace(Notes.DOUBLE_FLAT, Notes.DOUBLE_FLAT_M21))
                n = p.getEnharmonic().nameWithOctave
                note_ = MusicUtils.get_note(n)
            else:
                note_ = MusicUtils.get_note(anote)    # pitch+octave (default is 4)
            try:
                if "#" in note_:
                    ind = cnotes["sharp"].index(note_)
                elif "b" in note_:
                    ind = cnotes["flat"].index(note_)
                else:    # no accidental
                    ind = cnotes["sharp"].index(note_)
            except:
                ind = -1
            note_numbers[note_] = ind
        return note_numbers
    
    def distance(self, anote1:str, anote2:str)->int:
        """Returns the number of semitones (half-steps) separating 2 notes.
            For example, distance("D4", "C5") is 10, but distance("C5", "D4") is -10
        """
        dist = self.get_note_number(anote1, anote2)
        return dist[anote2]-dist[anote1]
    
    def compare_notes(self, anote1:str, anote2:str)->int:
        note_numbers = self.get_note_number(anote1, anote2)   # Dict[str,int]
        n1 = note_numbers[anote1]
        n2 = note_numbers[anote2]
        if n1 == n2:
            result = 0
        else:
            result = 1 if n2 > n1 else -1
        return result
        
        
    @staticmethod
    def notes_per_measure(time_signature:str, note_type:str):
        """ Calculate the number of a given note type are in one measure in a given time signature.
            Arguments:
                time_signature - as a string, for example "4/4" or "6/8"
                note_type - a music21 note type, "quarter", "eighth", "16th" etc.
            Returns the number of notes in one measure: TS BPM * (Note Type value / TS Note Value)
            For example, in 4/4 time and a note_type of "eighth", the note_type value is 8
            and the time signature note value (for a quarter note) is 4
            so the calculation is: 4 * (8/4) = 4 * 2 = 8.
        """
        ts = time_signature.split("/")
        ts_bpm = int(ts[0])    # beats per measure
        ts_type_value = int(ts[1])        # note value (type) that gets the beat
        note_type_value = Notes.NOTE_VALUES[note_type]
        notes_per_measure = ts_bpm * (note_type_value /ts_type_value)
        return notes_per_measure
    
def main():
    notes = Notes()
    chromatic_notes = notes.chromatic_notes
    print(chromatic_notes["sharp"])
    anote1 = "D3"
    anote2 = "F#4"
    note_numbers = notes.get_note_number(anote1, anote2)
    print(f" {anote1}, {anote2}  note numbers: {note_numbers}")
    dist1 = notes.distance(anote1, anote2)
    dist2 = notes.distance(anote2, anote1)
    print(f"distance from {anote1} to {anote2}: {dist1}")    # 16 is the right answer
    print(f"distance from {anote2} to {anote1}: {dist2}")    # -16

    
if __name__ == '__main__':
    main()
