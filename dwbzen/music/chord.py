'''
Created on Mar 3, 2021

@author: don_bacon
'''
import json, copy
from music.key import Key
from music.instruments import Instruments
from music.musicUtils import MusicUtils
from music21 import chord, note, metadata, pitch, tempo
from music21 import stream, interval, instrument, clef
from music21 import meter, duration
import music21
from typing import List, Dict, Union

class Chord(object):
    
    C_MAJOR_KEY = { "name" : "C-Major", "alternate_name" : "C major", "mode" : "Major", "accidental" : "mixed", "signature" : 0, "relativeKey" : "A-Minor" }
    DEFAULT_ROOT_PITCH = "C4"    # middle C
    INTERVALS = None    # set dynamically

    def __init__(self, chord_data:dict, root_pitch:str="C", key:Key=None, fmt=None):
        """
        Create a Chord instance from a dictionary, for example: 
        {"name":"Major seventh",  "symbols":["maj7","M7"],   "groups":["seventh"], 
           "formula":[4,3,4],     "intervals":["M3","m3","M3"], "size":3, 
           "chordSize":4,         "formulaNumber":2193,     "spelling":"C E G B" },
        Arguments:
            chord_data - a dictionary with the above structure.
            root_pitch - the root note of the chord. Default is 'C'. May include an octave designation.
            key - an optional Key instance. If None, the Key is set to C-Major.
        The chord_data["spelling"] are the notes of the chord with 'C' as the root.
        The notes of a chord can be constructed from the formula or intervals.
        """
        print(f"chord data: {chord_data}")
        self.chord_data = chord_data
        self._fmt = "condensed" if fmt is None else fmt
        self._name = self.chord_data['name']
        self._formula = self.chord_data['formula']           # intervals from the root as number of semitones
        self._formulaNumber = self.chord_data["formulaNumber"]
        self._intervals = self.chord_data['intervals']       # intervals from the root as interval names (quality+size)
        self._spelling = self.chord_data['spelling'].split()    # the chord notes, delimited by spaces, with C as the root
        # TODO; add support for extended format. For example, the notes of a C7 chord ( C E G Bb D )
        # would be C4 E4 G4 Bb4 D5, given a root of C4
        #
        _notes = copy.copy(self._spelling)    # the notes of the chord with a root of "C"
        self._symbols = self.chord_data['symbols']
        self.size = len(self.formula)
        self._key = Key(Chord.C_MAJOR_KEY) if key is None else key
        self._music21Key = None      # key.KeySignature
        
        music21Chord = chord.Chord(_notes)    # chord.Chord
        rootPitch = music21Chord.root().name.replace("-","b")
        rp = MusicUtils.get_pitch(root_pitch)     # given root with the octave stripped
        if rootPitch != rp:
            #
            # if a rootPitch is given and NOT "C", need to transpose the chord to the new root
            # p1 = pitch.Pitch("C"), p2=pitch.Pitch(rootPitch), aInterval =interval.Interval(pitchStart=p1,pitchEnd=p2)
            # then m21Chord = music21Chord.transpose(aInterval)
            #
            p2 = pitch.Pitch(rp)    # music21 treats a 'b' as a flat and converts to '-'
            p1 = pitch.Pitch(rootPitch)
            aInterval = interval.Interval(pitchStart=p1,pitchEnd=p2)
            m21Chord = music21Chord.transpose(aInterval)
            self._notes = list()
            for note in m21Chord.notes:
                self._notes.append(note.pitch.name.replace("-","b"))
            self._music21Chord = m21Chord
            self._rootPitch = m21Chord.root()
            self._root = m21Chord.root().name.replace("-","b")
        else:
            self._notes = _notes
            self._music21Chord = music21Chord
            self._root = rootPitch
            self._rootPitch = self._music21Chord.root()    # music21.pitch.Pitch
        
        
        print(f"chord root: {self._root}")
        print(f"notes: {self._notes}")
    
    @staticmethod
    def get_chord_notes(rootPitch:str, formula:Union(List[int], List[str]), compressed:bool=False, inversion:int=0)->List[str]:
        """Get the notes of a Chord given the root note and the formula.
            Arguments:
                rootPitch - the root note of the chord. If an octave is not present, octave 4 is used.
                formula - the chord formula as a list of number of semitones (half-steps) from each note.
                    OR a list of intervals, for example ["M3","m3","m3"] for a dominant 7th.
                    For example the formula for a dominant 9th is [4,3,3,4].
                    So starting with C4: C4 + 4 semitones is E4, E4 + 3 semitones is G4, etc.
                compressed - if True, the notes are all kept in the same octave.
                    In this form, the notes of D9 are D4,E4,F#4,A4,C5
                    Otherwise the notes are D4,F#4,A4,C5,E5
                inversion - invert the final chord (essentially rotate) by the number of places.
                    Default is 0, any int value is valid. For example 1st inversion, set inversion=1.
            Note - the implementation uses the music21 Pitch API.
        """
        chord_notes = list()
        rp = MusicUtils.get_note(rootPitch)    # add the octave if not present
        for f in formula:       # str or an int
            if isinstance(f, str):  #  an interval name
                pass
            elif isinstance(f,int) or isinstance(f, float):     # number of half-steps
                pass

        if inversion != 0:
            pass
        
        return chord_notes
    
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
    def music21Chord(self)->chord.Chord:
        return self._music21Chord
            
    @property
    def music21Key(self)->music21.key.Key:
        return self._music21Key
        
    @property
    def rootPitch(self)->pitch.Pitch:
        return self._rootPitch
    
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
            cls.INTERVALS = {
                "P1":0, "a1":1, "M2":2, "m2":1, "d2":0, "a2":3, "M3":4, "m3":3, "d3":2, "a3":5,
                "P4":5, "d4":4, "a4":6, "P5":7, "d5":6, "a5":8, "M6":9, "m6":8, "d6":7, "a6":10,
                "M7":11, "m7":10, "d7":9, "a7":12, "P8":12, "d8":11, "a8":13 }
        return cls.INTERVALS

    
    def show(self, format_:str, root="C4", octaves=1, notes:List[str]=None, note_duration="quarter", 
             instrument_name="Piano", second_part_transpose:int=0, metronome_mark:(int,str)=(100,"quarter"), time_signature:str="4/4"):
        
        if format_ == "notes":
            print(self.notes(root))
            return
        elif format_ == "pitches":
            print(self.pitches(root))
            return
        
        transpose_interval = interval.Interval(0)
        if instrument_name == "Piano":
            part_instrument = instrument.Piano()
        else:    # need to load Instruments and Clefs data
            instruments = Instruments()
            if instrument_name in instruments.instrument_names:
                part_instrument = instruments.get_instrument(instrument_name)
                interval_semitones = 0 if part_instrument.transposition is None else -part_instrument.transposition.semitones
                transpose_interval = interval.Interval(interval_semitones)
                part_instrument
            else:
                raise(TypeError(f"No dota for {instrument_name}"))
            
        part_tempo = tempo.MetronomeMark(number=metronome_mark[0], referent=note.Note(type=metronome_mark[1]))
        timeSignature = meter.TimeSignature(time_signature)
        part_clef = MusicUtils.getClef(root, octaves)
        part_stream = stream.Stream()
        part_stream.insert(0, metadata.Metadata())
        part_stream.metadata.title = self.name
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
        