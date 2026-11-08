'''
Created on Mar 3, 2021

@author: don_bacon
'''
import json, copy
from music.key import Key
from music.instruments import Instruments
from music.musicUtils import MusicUtils
from music.generalUtils import GeneralUtils
from music21 import chord, note, metadata, pitch, tempo
from music21 import stream, interval, instrument, clef
from music21 import meter, duration
import music21
from typing import List, Dict
from itertools import accumulate
import operator
from enum import Enum

class ChordPosition(Enum):
    """ChordPosition is how the notes of a chord are arranged.
        For example, a dominant 9th has the intervals: M3, m3, m3, M3 or formula 4,3,3,4.
        In CLOSED position the notes are all within a single octave range.
            The notes of a C9 with root C4 are C4,D4,E4,G4,Bb4
        In EXTENDED position the notes are defined strictly by intervals. 
            The notes of a C9 in EXTENDED position with root C4 are C4,E4,G4,Bb4,D5
        OPEN and SEMI_CLOSED are music21 positions defined by chord.Chord.openPosition()
        and chord.Chord.semiClosedPosition().
        If unspecified the default ChordPosition is EXTENDED.
    """
    CLOSED = "closed"           # also a music21 closedPosition
    EXTENDED = "extended"
    OPEN = "open"
    SEMI_CLOSED = "semi-closed" # music21 semiClosedPosition
    
class Chord(object):
    
    C_MAJOR_KEY = { "name" : "C-Major", "alternate_name" : "C major", "mode" : "Major", "accidental" : "mixed", "signature" : 0, "relativeKey" : "A-Minor" }
    DEFAULT_ROOT_PITCH = "C4"    # middle C
    INTERVALS = None    # set dynamically

    def __init__(self, chord_data:dict,/, root_pitch:str="C4", symbol:str=None, key:Key=None, position:ChordPosition=None, inversion=0, doubleRoot=False):
        """
        Create a Chord instance from a dictionary, for example: 
        {"name":"Major seventh",  "symbols":["maj7","M7"],   "groups":["seventh"], 
           "formula":[4,3,4],     "intervals":["M3","m3","M3"], "size":3, 
           "chordSize":4,         "formulaNumber":2193,     "spelling":"C E G B" }
        Arguments:
            chord_data - a dictionary with the above structure.
            root_pitch - the root note of the chord. Default is 'C4'.The octave designation is set to 4 if not included.
            symbol - an optional chord symbol. If present it overrides the symbol give in chord_data.
            key - an optional Key instance. If None, the Key is set to C-Major.
            position - a ChordPosition: How to construct the chords: CLOSED, EXTENDED, OPEN, or SEMI_CLOSED. 
            inversion - chord inversion as an integer - this rotates the notes to the right or left by that number of places, default is 0.
            doubleRoot - if True double the root note (add an additional note 1 octave higher than the root). True by default.
        The chord_data["spelling"] are the notes of the chord with 'C' as the root. 
        The notes in the chord spelling don't include an octave designation - an EXTENDED position is assumed.
        The notes of a chord can be constructed from the formula or intervals.
        All the chord_data fields are defaulted to produce a C-Major triad.
        """
        self.chord_data = chord_data
        self._position = ChordPosition.EXTENDED if position is None else position
        self._name = self.chord_data.get('name', "MajorChord")
        formula = self.chord_data.get("formula", [4,3])      # intervals from the root as number of semitone. Default of [4,3] is a Major triad
        self._formula = formula
        self._formulaNumber = self.chord_data.get("formulaNumber", 145)
        self._intervals = self.chord_data.get("intervals", ["M3","m3"])     # intervals from the root as interval names (quality+size)
        
        self._spelling = self.chord_data.get("spelling", "").split()    # the chord notes, delimited by spaces, with "C" as the root
        self._symbols:List[str] = self.chord_data.get("symbols", ["M"])
        self._symbol = self._symbols[0] if symbol is None else symbol  # the first symbol is the primary if not explicitly given
        self.size = len(self.formula)
        self._key = Key(Chord.C_MAJOR_KEY) if key is None else key
        self._music21Key = None      # key.KeySignature
        #
        _notes = Chord.chord_notes_from_formula(root_pitch, formula, position, doubleRoot)
        self._root = _notes[0]
        self._bassNote = self._root    # An inversion keeps the root and update the bass note.
            
        self._music21Chord = chord.Chord(_notes)    # music21 chord.Chord
        self._notes = _notes
        self._rootPitch = pitch.Pitch(root_pitch)
        self._doubleRoot = doubleRoot
        
        if inversion > 0:
            self.create_inversion(inversion)
        else:
            self._inversion = 0
        
        print(f"chord root: {self._root}")
        print(f"notes: {self._notes}")
    
    @staticmethod
    def chord_notes_from_formula(rootPitch:str, formula:List[int], position:ChordPosition=ChordPosition.EXTENDED, doubleRoot=False)->List[note.Note]:
        """Get the notes of a Chord given the root note and the formula.
            Arguments:
                rootPitch - the root note of the chord. If an octave is not present, octave 4 is used.
                formula - the chord formula as a list of number of semitones (half-steps) from each note.
                    For example the formula for a dominant 9th is [4,3,3,4].
                    So starting with C4: C4 + 4 semitones is E4, E4 + 3 semitones is G4, etc.
                inversion - invert the final chord (essentially rotate) by the number of places.
                    Default is 0, any int value is valid. For example 1st inversion, set inversion=1.
                    A C7 chord (formula [4,3,3] = C4,E4,G4,Bb4) in 1st inversion would be E4 G4 B-5 C5
                    A C9 (formula [4,3,3,4] = C4,E4,G4,Bb4,D5) in 1st inversion would be E4 G4 B-5 D5 C5
                position - ChordPosition instance, default value if not specified is ChordPosition.EXTENDED
                doubleRoot - if True double the root note (add an additional note 1 octave higher than the root). True by default.
            Returns: a List of music21 note.Note
        """
        rp = MusicUtils.get_note(rootPitch)    # add the octave if not present, default is octave 4
        rootNote= note.Note(rp)
        chord_notes = [rootNote]
        semitones = list(accumulate(formula, operator.add))
        
        for semitone in semitones:   # number of semitones from the root pitch
            st = semitone if position == ChordPosition.EXTENDED or position == ChordPosition.OPEN else semitone%12
            nextNote = rootNote.transpose(st)
            chord_notes.append(nextNote)
        if doubleRoot:
            chord_notes.append(rootNote.transpose("P8"))
        
        return chord_notes
    
    @staticmethod
    def music21_chord_from_formula(rootPitch:str, formula:List[int], inversion:int=0)->chord.Chord:
        """Create and return a music21.chord from the formula provided.  """
        chord_notes = Chord.chord_notes_from_formula(rootPitch, formula, inversion)
        m21Chord = chord.Chord(chord_notes)
        return m21Chord
    
    @staticmethod
    def get_formula_from_intervals(intervals:List[str])->List[int]:
        """ Get the chord formula corresponding to a list of interval names """
        sizesMap = MusicUtils.get_interval_sizes()
        formula:List[int] = list()
        for intName in intervals:
            intSize = sizesMap.get(intName,0)
            formula.append(intSize)
        return formula
    
    @staticmethod
    def chord_notes_from_intervals(rootPitch:str, intervals:List[str], inversion:int=0)->List[note.Note]:
        """Get the notes of a Chord given the root note and the formula.
            Arguments:
                rootPitch - the root note of the chord. If an octave is not present, octave 4 is used.
                intervals - the interval names comprising the chord for example ["M3","m3","m3"] for a dominant 7th.
                inversion - invert the final chord (essentially rotate) by the number of places.
                    Default is 0, any int value is valid. For example 1st inversion, set inversion=1.
            Note - the implementation uses the music21 Pitch API.
        """
        formula = Chord.get_formula_from_intervals(intervals)
        chord_notes = Chord.chord_notes_from_formula(rootPitch, formula, inversion)
        return chord_notes
    
    @staticmethod
    def music21_chord_from_intervals(rootPitch:str, intervals:List[str], inversion:int=0)->chord.Chord:
        """Create and return a music21.chord from the list of interval names provided.  """
        chord_notes = Chord.chord_notes_from_intervals(rootPitch, intervals, inversion)
        m21Chord = chord.Chord(chord_notes)
        return m21Chord
    
    def notes(self)->List[str]:
        return self._notes
    
    def pitches(self)->List[str]:
        return self._notes
    
    @property
    def spelling(self)->List[str]:
        return self._spelling
    
    @property
    def name(self)->str:
        return self._name
    
    @property
    def symbols(self)->List[str]:
        return self._symbols
    
    def add_symbol(self, symbol:str)->List[str]:
        self._symbols.append(symbol)
        return self._symbols
    
    @property
    def symbol(self)->str:
        return self._symbol
    
    @property
    def intervals(self)->List[str]:
        return self._intervals
    
    @property
    def root(self)->str:
        return self._root
    
    @property
    def formula(self)->List[int]:
        return self._formula
    
    @property
    def formulaNumber(self)->int:
        return self._formulaNumber
    
    @property
    def key(self)->Key:
        return self._key
    
    @key.setter
    def key(self, newKey):
        self._key = newKey
        self._music21Key = self._get_music21_key()
    
    @property
    def position(self)->ChordPosition:
        return self._position
    
    @position.setter
    def position(self, newPosition:ChordPosition):
        self._position = newPosition
    
    @property
    def music21Chord(self)->chord.Chord:
        if self._position == ChordPosition.CLOSED:
            self._music21Chord.closedPosition(inPlace=True)
        elif self._position == ChordPosition.SEMI_CLOSED:
            self._music21Chord.semiClosedPosition(inPlace=True)
        return self._music21Chord
            
    @property
    def music21Key(self)->music21.key.Key:
        return self._music21Key
        
    @property
    def rootPitch(self)->pitch.Pitch:
        return self._rootPitch
    
    @property
    def bassNote(self)->pitch.Pitch:
        return self._bassNote
    
    @bassNote.setter
    def bassNote(self, new_bassNote:str|pitch.Pitch)->None:
        bassNote = MusicUtils.get_note(new_bassNote)    # adds an octave if not present
        self._bassNote = pitch.Pitch(new_bassNote) if isinstance(new_bassNote,str) else new_bassNote
    
    def _get_music21_key(self, transpose_interval:interval.Interval|None=None)->music21.key.Key:
        """ 
        """
        if self._music21Key is None:
            self._music21Key = MusicUtils.get_music21_key(self._key, transpose_interval)
        return self._music21Key
    
    @classmethod
    def getIntervals(cls)->Dict(str,int):
        """Returns a mapping of interval names to number of semitones (half steps).
            An interval is the distance between 2 notes. For example, "M3" (a major 3rd) is 4 semitones (half-steps).
            Interval names use the standard naming convention of quality + size
            quality :: "M", "m", "P", "d", "a" for major, minor, perfect, diminished, and augmented
            size :: an integer from 1 to 8 for unison, 2nd, 3rd etc. up to an octave
            If the upper note in an interval has not been altered chromatically, the interval will be major or perfect.
            If it has been altered it will be minor, diminished or augmented. The following table summarizes:
            Diatonic interval    Altered Chromatically    New Interval
            major                half step larger         augmented
            perfect              half step larger         augmented
            major                half step smaller        minor
            minor                half step smaller        diminished
            perfect              half step smaller        diminished
        """
        if cls.INTERVALS is None:
            cls.INTERVALS = MusicUtils.get_interval_sizes()
        return cls.INTERVALS
    
    def arpegiate(self)->List[note.Note]:
        """ Create a list of Note from the notes in this chord
        """
        notes = [note for note in self._music21Chord.notes]
        return notes
    
    def create_inversion(self, inversion:int)->None:
        # TODO 
        """ Create an inversion of this chord and update the symbol as a slash chord:
            For example: D4  F#4  A4  C4  E5  =>  F#4  A4  C4 D5  E5
            D9 formula: 4,3,3,4   1st inversion symbol 'D9/F#', C9 in 1st inversion is 'C9/E'
            Argument:
                inversion - a positive integer with range from 1 to len(self.formula).
                    If inversion < 0, the absolute value is used.
                For example a major triad (4,3) has 2 inversions.
            Note that this updates self directly.
        """
        self._inversion = abs(inversion%len(self._notes))
        inversion = self._inversion
        while inversion > 0:
            bass_note = self._notes[0]
            self._notes.append(bass_note.transpose("P8"))
            self._notes = self._notes[1:]
            inversion-=1

        self._bassNote = self._notes[0]
        self._symbol = f"{self._symbol}/{self._bassNote.name}"
        self._music21Chord = chord.Chord(self._notes)    # music21 chord.Chord


    def __iter__(self):
        return self.arpegiate().__iter__()
    
    def show(self, format_:str, root="C4", octaves=1, notes:List[str]=None, note_duration="quarter", 
             instrument_name="Piano", second_part_transpose:int=0, metronome_mark:(int,str)=(100,"quarter"), time_signature:str="4/4"):
        
        if format_ == "notes":
            print(self.notes(root))
            return
        elif format_ == "pitches":
            print(self.pitches(root))
            return
        
        part_instrument,transpose_interval = GeneralUtils.get_instrument(instrument_name)
            
        part_tempo = tempo.MetronomeMark(number=metronome_mark[0], referent=note.Note(type=metronome_mark[1]))
        timeSignature = meter.TimeSignature(time_signature)
        part_clef = MusicUtils.getClef(root, octaves)
        part_stream = stream.Stream()
        part_stream.insert(0, metadata.Metadata())
        part_stream.metadata["title"] = f"{self.name}\n{self._root.name}{self.symbol}"

        part_stream.insert(part_clef)
        part_stream.insert(self._get_music21_key(transpose_interval))
        part_stream.insert(timeSignature)
        part_stream.insert(part_tempo)
        part_stream.insert(0, part_instrument)
        dur = duration.Duration()
        dur.type = note_duration
        self._music21Chord.duration = dur
        part_stream.append(self._music21Chord)
        part_stream.show(fmt=format_)

if __name__ == '__main__':
    c13_chord_data = {"name":"Dominant thirteenth", "symbols":["13"], "groups":["extended"], "formula":[4,3,3,4,7],
                  "intervals":["M3", "m3", "m3", "M3", "P5"], "size":5, "chordSize":6, "formulaNumber":1685, "spelling":"C E G Bb D A" }
    c9_chord_data = {"name":"Dominant ninth", "symbols":["9"], "groups":["extended"], "formula":[4,3,3,4], 
                   "intervals":["M3", "m3", "m3", "M3"], "size":4, "chordSize":5, "formulaNumber":1173, "spelling":"C E G Bb D" }
    
    c13 = Chord(c9_chord_data, root_pitch="C4", position=ChordPosition.EXTENDED)
    c13.show(format_="musicxml", note_duration="half")
    for note in c13: print(note)
    