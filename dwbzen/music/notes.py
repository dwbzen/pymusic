'''
Created on Sep 22, 2026

@author: don_bacon
'''
from functools import cached_property
from typing import Dict, List
from music.musicUtils import MusicUtils
from music21 import pitch, note

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
            The octave range is num_octaves set in the constructor which defaults to 10
        """
        num_octaves = self.num_octaves
        cpf = num_octaves * Notes.FLAT_PITCHES       # 12 pitches x #octaves
        cps = num_octaves * Notes.SHARP_PITCHES
        cpm = num_octaves * Notes.MIXED_PITCHES
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
    
    def get_pitch_number(self, *pitches):
        note_numbers = {}
        cnotes = self.chromatic_pitches
        for anote in pitches:
            if Notes.DOUBLE_SHARP in anote:
                p = pitch.Pitch(anote)
                n = p.getEnharmonic().nameWithOctave
                note_ = MusicUtils.get_pitch(n)
            elif Notes.DOUBLE_FLAT in anote:
                p = pitch.Pitch(anote.replace(Notes.DOUBLE_FLAT, Notes.DOUBLE_FLAT_M21))
                n = p.getEnharmonic().nameWithOctave
                note_ = MusicUtils.get_pitch(n)
            else:
                note_ = MusicUtils.get_pitch(anote)    # pitch+octave (default is 4)
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
    
    def get_note_number(self, *notes):
        note_numbers = {}
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
                    ind = self.chromatic_notes["sharp"].index(note_)
                elif "b" in note_:
                    ind = self.chromatic_notes["flat"].index(note_)
                else:    # no accidental
                    ind = self.chromatic_notes["sharp"].index(note_)
            except:
                ind = -1
            note_numbers[note_] = ind
        return note_numbers
    
    def get_notes(self, start_index:int, end_index:int, num_sharps=1)->List[note.Note]:
        """ Get the notes by index.
            Arguments:
                start_index - an int >= 0
                end_index - also an int >=0
                num_sharps - indicates the key signature. If <0 this indicates the number of flats.
                    This is used to select the accidental to use.
                Note: if start_index < end_index, for example 20 to 30, the list is returned in reverse order.
            Returns:
                a list of note.Note : notes:List[note.Note]
        """
        indexes = [x for x in range(start_index,end_index+1)] if start_index < end_index else [x for x in range(end_index,start_index-1, -1)]
        chromaticNotes = self.chromatic_notes["sharp"] if num_sharps >= 0 else self.chromatic_notes["flat"]
        notes = list()
        for ind in indexes:
            anote = chromaticNotes[ind]
            notes.append(note.Note(anote))
        return notes
    
    def distance(self, start_note:str, end_note:str)->int:
        """Returns the number of semitones (half-steps) from one note to another.
            For example, distance("D4", "C5") is 10, but distance("C5", "D4") is -10
        """
        dist = self.get_note_number(start_note, end_note)
        return dist[end_note]-dist[start_note]
    
    def compare_notes(self, note1:str, note2:str)->int:
        """Compare two notes.
            Arguments:
                note1, note2 - note names representing the notes to compare, for example "D3", "F4"
            Returns
                0 if the notes are equal, 1 if note1 is > note2, -1 if note1 < note2
                What's compared are the chromatic note numbers.
                
        """
        note_numbers = self.get_note_number(note1, note2)   # Dict[str,int]
        n1 = note_numbers[note1]
        n2 = note_numbers[note2]
        if n1 == n2:
            result = 0
        else:
            result = -1 if n2 > n1 else 1
        return result
    
    def compare_pitches(self, pitch1:str, pitch2:str, relative_to:str="C"):
        pitch_numbers = self.get_pitch_number(pitch1,pitch2, relative_to)
        start_ind = pitch_numbers[relative_to]
        n1 = (start_ind + pitch_numbers[pitch1])%12
        n2 = (start_ind + pitch_numbers[pitch2])%12
        if n1 == n2:
            result = 0
        else:
            result = -1 if n2 > n1 else 1
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
    anote1 = "D3"
    anote2 = "F#4"
    note_numbers = notes.get_note_number(anote1, anote2)
    pitch1 = "A"
    pitch2 = "D"
    pitch_numbers = notes.get_pitch_number(pitch1,pitch2)
    print(f" {anote1}, {anote2}  note numbers: {note_numbers}")
    print(f" {pitch1}, {pitch2} pitch numbers: {pitch_numbers}")
    
if __name__ == '__main__':
    main()
