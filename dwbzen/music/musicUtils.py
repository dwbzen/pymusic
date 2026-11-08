

import music21
from music21 import interval, tempo, meter, stream, chord
from music21 import note, clef, duration, metadata, key, pitch
from music21.stream import Score
from music21.stream import Part
from music21.stream import Measure
from music.instruments import Instruments
from music.key import Key
from music.generalUtils import GeneralUtils
from common.environment import Environment

import json
import pathlib, random, copy, math, secrets
from datetime import date
from builtins import isinstance
from typing import List, Dict, Any, Union
from itertools import accumulate
import operator

class MusicUtils(object):
    """Music utilities
        TODO - some of the method names are confusing, like score_notes vs. notes_for_score etc. 
    """
    
    verbose = 0
    C_Major = key.Key('C')
    A_Minor = key.Key('a')
    default_pitch_map = {'Db':'C#', "D-":'C#', 'D#':'Eb', 'Gb':'F#', 'G-':'F#', 'Ab':'G#', 'A-':'G#', 'A#':'Bb' }
    THEORY_STRUCTURES = {}      # See theory.json for content
    environment:Environment = None
    INTERVAL_MAP = None
    INTERVAL_SIZE = None
    THEORY_FILENAME = "theory.json"
    DEFAULT_KEY = Key({ "name" : "C-Major", "alternate_name" : "C major", "mode" : "Major", "accidental" : "sharp", "signature" : 0, "relativeKey" : "A-Minor" })
    
    @staticmethod
    def get_enironment()->Environment:
        if MusicUtils.environment is None:
            MusicUtils.environment = Environment.get_environment()
        return MusicUtils.environment
    
    @staticmethod
    def get_theory()->dict:
        """Gets the structures in the theory.json file as a Dict """
        env = MusicUtils.get_enironment()
        resource_folder = env.get_resource_folder("music")
        theory_file = f"{resource_folder}/{MusicUtils.THEORY_FILENAME}"
        with open(theory_file, "r") as read_file:
            theory_data = json.load(read_file)
        return theory_data
    
    @staticmethod
    def get_interval_map()->Dict[int,str]:
        """Returns a Dict that maps an interval size to an interval name. For example: { 5:"P4", 7:"P5"}
            This returns the cached value if it is not None.
        """
        if MusicUtils.INTERVAL_MAP is None:
            theory_data = MusicUtils.get_theory()
            interval_map = theory_data["interval_map"]
            imap = {}
            for interval in interval_map.keys():
                imap[int(interval)] = interval_map[interval]
            MusicUtils.INTERVAL_MAP = imap
        return MusicUtils.INTERVAL_MAP
    
    @staticmethod
    def get_interval_sizes()->Dict[str,int]:
        """Returns a Dict that maps an interval name to the interval size (in semitones). For example: {3:"m3", 4:"M3"}
            M3 = major 3rd, m3 = minor 3rd
            This returns the cached value if it is not None
        """
        if MusicUtils.INTERVAL_SIZE is None:
            theory_data = MusicUtils.get_theory()
            interval_size_map = theory_data["interval_size"]
            MusicUtils.INTERVAL_SIZE = interval_size_map
        return MusicUtils.INTERVAL_SIZE
    
    @staticmethod
    def intervalNames_to_intervalSizes(interval_names:List[str]):
        """ Convert a list of interval names to a corresponding formula (list of sizes in semitones) """
        sizes:List[int] = list()
        int_sizes = MusicUtils.get_interval_sizes()
        for name in interval_names:
            sizes.append(int_sizes.get(name, 0))
        return sizes

    @staticmethod
    def intervalSizes_to_intervalNames(interval_sizes:List[int]):
        """ Convert a list of interval sizes to a corresponding list of interval names """
        names:List[str] = list()
        int_names = MusicUtils.get_interval_map()
        for isize in interval_sizes:
            names.append(int_names.get(isize, "d2"))
        return names
    
    @staticmethod
    def root_intervals(formula:List[int]):
        """ Converts a chord (or scale) formula to a list of intervals from a root note.
            A standard formula gives the semitones between successive notes.
            For example the formula for a dominant 9th chord is [4,3,3,4]
            As root intervals this is [4,7,10,14]
        """
        semitones = list(accumulate(formula, operator.add))
        return semitones
    
    @staticmethod
    def rotate(lst:List[Any], n)->List[Any]:
        """Positive n rotates left; negative n rotates right."""
        if not lst:
            return lst
    
        n %= len(lst)
        return lst[n:] + lst[:n]
        
    
    @staticmethod
    def formula_to_pitch_indexes(formula:List[int]):
        """
        Creates a List of relative pitch indexes from a given formula.
         Each element is the number of steps from the root.
         For example given the chord formula [4, 3, 3, 4] (a 9th chord)
         the resulting pitch set is [0, 4, 7, 10, 14]
         If the root Pitch is C, the corresponding Pitches are { C, E, G, Bb, D}
        """
        pitchSet:List[int] = [0]    # root
        pitchSet += MusicUtils.root_intervals(formula)
        return pitchSet
        
    
    @staticmethod
    def get_formulaNumber(formula:List[int]):
        """ Gets the forulaNUmber for a corresponding formula
            For example, the formula number for [4, 3, 3, 4] (a 9th chord) is 1173.
            The formula number is a binary representation of each element of the formula.
            1173 in binary is 10010010101.
        """
        fnum = 0
        indexes = MusicUtils.formula_to_pitch_indexes(formula)
        for pi in indexes:
            shiftamt = pi if pi < 12 else pi-12
            fnum += (1<<shiftamt)
        return fnum
    
    @staticmethod
    def get_notes_from_formula(formula:List[int], startingNote:str, key:Key=DEFAULT_KEY)->List[note.Note]:
        """ Gets the list of notes associated with a formulq.
            Arguments:
                formula - a List if int that give the intervals (in semitones) between notes
                startingNote - the root note as a string, if an octave is not specified octave 4 is used.
                key - optional music.Key, used to determine accidentals in the resulting notes.
            Returns:
                a List of note.Note (music21).
            BTW music21 note names use '-' for flats instead of "b" although the constructor takes either one.
        """
        start_note = MusicUtils.get_note(startingNote)    #adds the octave if not present
        isFlat = ("b" in key.key_name or key.key_name.startswith("C") )
        isSharp = not isFlat
        current_note:note.Note = note.Note(start_note)
        notes:List[note.Note] = [current_note]
        for ind in formula:
            next_note = current_note.transpose(ind)
            note_name = next_note.nameWithOctave
            if isFlat and "#" in note_name or isSharp and "-" in note_name:
                next_note.pitch = next_note.pitch.getEnharmonic()
            notes.append(next_note)
            current_note = next_note
        return notes
    
    @staticmethod
    def has_octave(note):
        return len(note) > 0 and note[len(note)-1].isdigit()

    @staticmethod
    def get_octave(note:str, default_octave=4)->int:
        """ Gets the octave designation of a given note.
            If the note is in scientific notation (as in C4 or Bb2), it returns the octave as an int.
            Otherwise it returns the default_octave argument, which defaults to 4.
        """
        if(MusicUtils.has_octave(note)):
            return  int(note[-1:])
        else:
            return default_octave

    @staticmethod
    def get_octaves(*notes)->List[int]:
        """ Gets the octave designation for a list of notes.
            Arguments:
                notes - variable number of note names.
            Returns a List[int] of the octave values of those notes.
                The octave value for a note that does not have an octave is -1.
        """
        return[MusicUtils.get_octave(note) for note in notes]

    @staticmethod
    def get_pitch(note:str|pitch.Pitch)->str|pitch.Pitch:
        """Strips the octave designation of a given note
            The return data type matches the data type of the note argument: str or Pitch
            If note instance is a Pitch, it sets note.octave to None.
            Raises a TypeError if note is not a string or Pitch
        """
        if isinstance(note, str):
            return note[:-1] if MusicUtils.has_octave(note) else note
        elif isinstance(note, pitch.Pitch):
            note.octave = None
            return note
        else:
            raise TypeError("Invalid data type")

    @staticmethod
    def get_note(note:str|pitch.Pitch, default_octave:int=4)->str|pitch.Pitch:
        """Adds an octave designation to a given note, default octave is 4
            but can be set to any int >=-1.
            Returns the input note if it already has an octave
            The return data type matches the data type of the note argument: str or Pitch
            Raises a TypeError if note is not a string or Pitch
        """
        if isinstance(note, str):
            return note if MusicUtils.has_octave(note) else  f"{note}{default_octave}"
        elif isinstance(note, pitch.Pitch):
            if note.name == note.nameWithOctave:    # need to add the octave if not present
                note.octave = default_octave
            return note
        else:
            raise TypeError("Invalid data type")
    
    @staticmethod
    def getNote(note:str)->(str,int):
        """ Adds an octave designation to a given note, default octave is 4
            but can be set to any int >=-1.
            Returns pitch,octave as a str,int pair.
        """
        pitch = MusicUtils.get_pitch(note)
        octave = int(MusicUtils.get_octave(note, default_octave=4))
        return pitch,octave
    
    @staticmethod
    def getClef(root:str, octaves:int=1)->clef.Clef:
        root_octave = MusicUtils.get_octave(root)
        top_octave = root_octave + octaves
        if 4 <= root_octave <=5:
            part_clef = clef.TrebleClef()
        elif root_octave > 5:
            part_clef = clef.Treble8vaClef()
        elif 2 <= root_octave <= 3:
            part_clef = clef.BassClef()
        else:
            part_clef = clef.Bass8vbClef()
        return part_clef

    @staticmethod
    def get_music21_key(key:Key, transpose_interval:interval.Interval|None)->key.Key:
        """ Create a music21.key.Key instance from a music.Key instance
            Arguments:
                key - a music.Key
                transpose_interval - optional, for transposing instruments such as a Clarinet.
                    This is the interval.Interval of transposition.
            Returns the music21.key.Key corresponding to the music.Key
        """
        accidental = -1 if key.accidental == "flat" else 1
        semitones = transpose_interval.semitones if transpose_interval is not None else 0
        signature = key.signature  * accidental  # number of sharps or flats, no need transpose the  key
        music21Key = music21.key.KeySignature(signature)
        _music21Key = music21Key if semitones == 0 else music21Key.transpose(semitones)
        return _music21Key
    
    @staticmethod
    def get_music21_note(anote:str, transpose_semitones=0):
        """Create and return a music21.note.Note from a given string.
            Arguments:
                anote - a pitch represented as a string, for example "C4"
                transpose_semitones - the number of semitones (up or down) to transpose the resulting Note.
        """
        m21Note = note.Note(anote)
        return m21Note if transpose_semitones == 0 else m21Note.transpose(transpose_semitones)

    
    @staticmethod
    def show( fmt:str, name:str=None, startingNote="C4", octaves=1, formula:List[int]=None, notes:Union(List[str], List[note.Note])=None, 
              note_duration="quarter", asChord:bool=True, key:Key=DEFAULT_KEY, 
              instrument_name="Piano", metronome_mark:(int,str)=(120,"quarter"), time_signature:str="4/4")->None:
        
        """ Display either a given formula or a list of notes (as strings or note.Note) in a given format.
            Arguments:
                fmt - output format: "pitches", "notes", "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf"
        """
        if name is None:
            myName = "MyChord" if asChord else "MyMelody"
        else:
            myName = name
        if notes is None or len(notes)==0:
            if formula is None or len(formula)== 0:
                notes_list = []
            else:
                notes_list = MusicUtils.get_notes_from_formula(formula, startingNote, key)
        else:
            if isinstance(notes[0], note.Note):
                notes_list = notes
            else:
                notes_list = [MusicUtils.get_music21_note(anote) for anote in notes]
        
        if len(notes_list)==0:
            print("\n")    # noting to see here
            return
        
        if fmt == "notes":
            disp = [f"{anote.nameWithOctave.replace('-','b')} " for anote in notes_list]
            print(disp)
        elif fmt == "pitches":
            disp = [f"{anote.name.replace('-','b')} " for anote in notes_list]
            print(disp)
        else:
            part_instrument,transpose_interval = GeneralUtils.get_instrument(instrument_name)
                
            part_tempo = tempo.MetronomeMark(number=metronome_mark[0], referent=note.Note(type=metronome_mark[1]))
            timeSignature = meter.TimeSignature(time_signature)
            part_clef = MusicUtils.getClef(startingNote, octaves)
            part_stream = stream.Stream()
            part_stream.insert(0, metadata.Metadata())
            part_stream.metadata["title"] = f"{myName}"
    
            part_stream.insert(part_clef)
            part_stream.insert( MusicUtils.get_music21_key(transpose_interval))
            part_stream.insert(timeSignature)
            part_stream.insert(part_tempo)
            part_stream.insert(0, part_instrument)
            dur = duration.Duration()
            dur.type = note_duration
            # self._
            # 
            if asChord: # Construct a music21.Chord from the notes or formula
                music21Chord = chord.Chord(notes_list)    # music21 chord.Chord
                music21Chord.duration = dur
                part_stream.append(music21Chord)
            else:
                for anote in notes_list:
                    anote.duration = dur
                    part_stream.append(anote)
            
            part_stream.show(fmt=fmt)


if __name__ == '__main__':
    interval_map = MusicUtils.get_interval_map()
    print(f"interval map: {interval_map}")
    interval_sizes = MusicUtils.get_interval_sizes()
    print(f"interval sizes: {interval_sizes}")
    formula = [4,3,3,4]
    startingNote = "Bb3"
    notes = MusicUtils.get_notes_from_formula(formula, startingNote)
    MusicUtils.show("notes", startingNote=startingNote, notes=notes)
    
