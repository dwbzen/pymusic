# ------------------------------------------------------------------------------
# Name:          scale.py
# Purpose:       Encapsulate a musical scale.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2026 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from typing import List, Dict, Union
from itertools import accumulate
import operator
import argparse
from textwrap import dedent
from music21 import stream, note, pitch, scale, metadata
from music21 import chord, instrument, tempo, meter, interval
from music.keys import Keys
from music.key import  Key
from music.instruments import Instruments
from music.musicUtils import MusicUtils
from music.generalUtils import GeneralUtils
from music.notes import Notes
from music.scaleLibrary import ScaleLibrary

class Scale:
    """  
    A single Scale as a dictionary with the keys:
    name - primary lookup key
    alternateNames - list of AKAs
    groups - list of group names the scale is a member of
    formula - a list of integer intervals that define the scale. 
        Given a root note, the first interval is number of half steps to raise that note to obtain the next note.
        Subsequent notes are obtained by raising the current note that number of half steps.
        For example, with a root note 'C', and the formula [2, 2, 1, 2, 2, 2, 1], the resulting notes are:
        C (+2) D (+2) E (+1) F (+2) G (+2) A (+2) B (+1) C. 
        The number of notes produced by a give formula is len(formula)+1. 
        For standard scales, The sum of the intervals in a given formula MUST equal 12 to span 1 octave.
    size - number of notes in the scale excluding the final note, which is an octave above the root.
        So the size of diatonic scales (major, harmonic minor, etc.) is 7.
        
    The API distinguishes pitch and note. A pitch is only the name of the pitch :: pitch name + accidental
    where pitch name is in [C,D,E,F,G,A,B] and accidental is "#" for sharps, and "b" for flats.
    Double sharps are indicated by 'x' or '##' so Cx is enharmonically equivalent to D.
    Double flats are indicated by 'bb' so 'Ebb' is enharmonically equivalent to D.
    A note is a pitch in scientific pitch notation. This places "C4" as middle C, preceded by "B3"
    The range of a 88-key piano is A0 to C7.
    
    Note ordering is determined by scientific notation ordering: A0, A#0, B0, C1, C#1, ... B6, B7 etc.
    Pitch ordering (no octave designations) are relative to a chromatic scale starting on a given root pitch, default is 'C'
    So given a root of 'A', the scale is [A,A#,B,C,C#,... G#] witch is basically alphabetic ordering. Here 'C' > 'A'
    Given a root of 'C', the scale is [C,C#,D,...A,A#,B]. Here 'C' < 'A'
    By rule, when comparing 2 pitch/notes, they must both either include the octave or not include the octave.
    """
    
    DEFAULT_KEY = Key({ "name" : "C-Major", "alternate_name" : "C major", "mode" : "Major", "accidental" : "sharp", "signature" : 0, "relativeKey" : "A-Minor" })
    notes_ = Notes()
        
    def __init__(self, scaleData:Union(Dict,str), key:Key=None, octaves:int=1, descending:bool=False, formula:List[int]=None, custom=False):
        """
        Create a Scale from a dictionary
        Arguments:
            scale_data a dict representing a single scale having the keys described above
                for example: { "name" : "Major" , "groups" : [ "major", "diatonic", "common"] , "formula" : [2,2,1,2,2,2,1] , "size" : 7}
                OR the name of a scale. The scale_data argument is mandatory.
            key - optional Key object. Defaults to C-Major if not provided.
                The Key is used to determine the accidental choice. 
                Also the root note of the scale is the tonic note of the key.
            octaves - the number of octaves to cover. Range is 1 to 4, default is 1.
            descending - if True create the scale in descending order. Default is False
            formula - a user-defined scale formula as a List[int]. If present this overrides any scaleData.
            custom - if True this scale/melody is not in the scale library
        Note a music21.scale.ConcreteScale is also created as needed.
        """
        assert(scaleData is not None)
        self._key = Key(key_data=Scale.DEFAULT_KEY) if key is None else key
        
        self.octaves = octaves
        self.descending = descending
        if isinstance(scaleData, str):    # the name of a scale
            # if there is a formula us it instead of the name
            if formula is not None and len(formula) >=2:
                print(f"Using the formula {formula}")
            scaleLib = ScaleLibrary()
            scale_data = scaleLib.getScaleData(scaleData)
            if scale_data is None:    # Create something
                scale_data = {"name":scaleData, "groups":["custom"], "formula":formula, "size":len(formula)}
            self.scale = scale_data
            self.scale_data = scale_data
        elif isinstance(scaleData, dict):
            self.scale = scaleData
            self.scale_data = scaleData
        else:
            raise(TypeError("Invalid scale data"))
        
        self._name = self.scale.get('name', "MyScale")
        self._formula = self.scale.get('formula', [])
        self._custom = custom
        self._size = self.scale.get("size", 0)
        self._groups = self.scale.get("groups", [])
        self._alternate_names = self.scale.get("alternateNames", [])
        self._music21Scale = None    # music21.scale.ConcreteScale
        self._music21Key = None      # key.KeySignature
        self._notes = Notes()
    
    @staticmethod
    def get_chromatic_pitches_for_key(key:Key, ascending:bool=True)->List[str]:
        """ Returns a list of chromatic pitches for the Key provided.
            Arguments:
                key - a valid Key object.
                ascending - set to True, the default, if an ascending scale is desired, False for descending.
            Returns the appropriate chromatic pitches: CHROMATIC_SHARP_PITCHES or CHROMATIC_FLAT_PITCHES
            
            For example given a key of Ab Major (4 flats: B,E,A,D) ascending,
            the result would be 'C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B' (over 4 octaves)
            For a key of A Major (3 sharps: F,C,G) descending the result would be also be CHROMATIC_FLAT_PITCHES.
            Note that Key("C-Major") is treated as a sharps key.
         """
        if ascending:
            chromatic_pitches = Scale.notes_.get_chromatic_flat_pitches() if key.accidental.startswith("flat") else Scale.notes_.get_chromatic_sharp_pitches()
        else:
            chromatic_pitches = Scale.notes_.get_chromatic_sharp_pitches() if key.accidental.startswith("flat") else Scale.notes_.get_chromatic_flat_pitches()
        return chromatic_pitches
    
    @staticmethod
    def enharmonic_equivalent(pitch_:str)->(str,pitch.Pitch):
        """ Returns the enharmonic equivalent (EE) of a given pitch.
            The pitch may include an octave.
            The implementation creates a music21.pitch.Pitch instance and
            then uses the getEnharmonic() function.
            Returns a duple: str(enharmonic_equivalent), enharmonic_equivalent which is a music21 pitch.Pitch
            
            Some examples: EE of C# is Db, EE of Gb is F3, EE of C is B#, EE of E is Fb.
            Use of double sharps and flats is valid so EE(C##) is D, EE(Cbb) is Bb.
            This also supports pitches in scientific notation. For example, EE('Cb4') is 'B3'
        """
        p = pitch_.replace("b", "-")    # music21 uses - instead of b for a flat
        m21_pitch = pitch.Pitch(p)
        enharmonic_equivalent = m21_pitch.getEnharmonic()
        ee = str(enharmonic_equivalent).replace("-","b")
        return ee,enharmonic_equivalent
    
    @staticmethod
    def get_pitch_set(formula:List[int], root_pitch:str="C", accidental:str=None, include_octave=False)->dict:
        """
        Creates a List of relative pitch indexes, and a list of pitches for a given formula
        Each element is the number of steps from the root of the root_pitch provided, default root_pitch is 'C'.
        For example given the scale formula  [1, 2, 1, 2, 1, 2, 2, 1] (name == 'Shostakovich respelled all sharp')
        the resulting pitch set is [0, 1, 3, 4, 6, 7, 9, 11, 12] 
        If the root Pitch is C, the corresponding pitches are ['C', 'C#', 'Eb', 'E', 'F#', 'G', 'A', 'B']
        Arguments:
            formula - the scale formula as a List[int].
            root_pitch - the starting note to use
            accidental is the accidental to use when creating pitches. If None (the default) the cromatic
                pitch set to use is based on the root_pitch. Otherwise specify "#' or "b".
            include_octave - if True, add the root_pitch at the end, representing a full octave.
                default is False.
        Returns a dict with keys "pitch_set" (the index of chromatic notes in the scale), and "pitches"
        """
        pitch_set = list(accumulate(formula, operator.add, initial=0)) if include_octave else list(accumulate(formula, operator.add, initial=0))[:-1]
        tonic:pitch.Pitch = MusicUtils.get_pitch(root_pitch)
        
        if "b" in  tonic or accidental == "b":
            cps = Scale.notes_.get_chromatic_flat_pitches()
            ind = cps.index(tonic)
            pitches = [cps[x+ind] for x in pitch_set]
            
        elif "#" in tonic or accidental == "#" or tonic[0] in "GDAEB":    # there's # in the tonic or it's the root of a sharp key
            cps = Scale.notes_.get_chromatic_sharp_pitches()
            ind = cps.index(tonic.upper())
            pitches = [cps[x+ind] for x in pitch_set]
            
        else:
            cps = Scale.notes_.get_chromatic_flat_pitches()
            ind = cps.index(tonic)
            pitches = [cps[x+ind] for x in pitch_set]
            
        return {"pitch_set" : pitch_set, "pitches" : pitches}
    

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
    def key(self)->Key:
        return self._key
        
    @property
    def formula(self)->List[int]:
        return self._formula

    @property
    def music21Scale(self)->scale.ConcreteScale:
        return self._music21Scale
    
    @formula.setter
    def formula(self, newformula):
        self.formula = newformula
        self.size = len(newformula)
    
    def compare_notes(self, note1:str, note2:str, root:str=None)->int:
        """ Compare 2 notes or pitches relative to a chromatic scale starting on a given root pitch
            Arguments:
                note1 - note to compare. May or may not include the octave.
                note2 - note to compare against note1. May or may not include the octave.
                root - starting note (includes the octave, as in "C#4") or pitch (no octave, as in "Db").
                        If not specified the root defaults to "C" or "C4".
                Note that both notes AND the root must either include the octave or not.
            Returns:
                -1 if note1 < note2
                1 if note1 > note2
                0 if note1 == note2
            Examples:
            1. Given a root of "A", note1 is "B", note2 is "C", the result is -1
                because the scale is A,B,C,D,E,F,G (omitting accidentals) and B comes before C.
               If the root was "C", the result would be 1 because in the scale
                C,D,E,F,G,A,B,C  B comes after C.
            2. The octave is used if both notes include it. 
            Raises a TypeError if the arguments are inconsistent or don't represent notes.
        """
        result = 0
        root = "C" if root is None else root
        # 0==no note octaves, 2==both notes have octaves, 1==one does, one doesn't, invalid
        octaves = MusicUtils.has_octave(note1) + MusicUtils.has_octave(note2)
        if octaves == 1:    # they must all have octave or not
            raise(TypeError("All arguments must include an octave or not"))
        if octaves == 2:
            # a root note is not needed is both notes are is scientific notation (have octaves)
            return self._notes.compare_notes(note1, note2)
        if octaves == 0:   # compare 2 pitches relative to a chromatic scale whose starting note is root
            return self._notes.compare_pitches(note1, note2, relative_to=root)
            
        return result
    
    def _create_music21_scale(self, tonic:str, pitches:List[str])->scale.ConcreteScale:
        """ Create a music21 ConcreteScale from a list of pitches.
            Arguments:
                tonic - the tonic note of the scale as a pitch or note (pitch+octave)
                pitches - a list of pitches as List[str]
            Sets m21Scale property
        """
        m21Pitches = [x.replace("b","-") for x in pitches]
        self._music21Scale = scale.ConcreteScale(tonic=tonic, pitches=m21Pitches)
    
    def get_music21_key(self, transpose_interval:interval.Interval|None)->key.Key:
        """ Create a music21.key.Key instance from a music.Key instance
            Arguments:
                transpose_interval - optional, for transposing instruments such as a Clarinet.
                    This is the interval.Interval of transposition.
            Returns the music21.key.Key corresponding to the music.Key
            Also sets the result as self._music21Key
        """
        if self._music21Key is None:
            self._music21Key = MusicUtils.get_music21_key(self.key, transpose_interval)
        return self._music21Key
        

    def notes(self, root='C4', num_octaves:int=1, add_descending:bool|None=None)->List[str]:
        """
        Creates and returns the list of notes for this scale starting with the root provided. 
        Arguments:
        root - the default root is 'C4' (middle C).
            If the root provided lacks an octave, 4 is assumed.
            By convention, notes are expressed in scientific music notation which includes an octave designation starting at 0
            For example, the range of a Piano is A0 to C8.
            Octaves are from C to B, so the pitch following B4 is C5.
            In general the accidental (# or b) used is determined by the key.
            
        add_descending - if not None, this overrides the value of self.descending
        
        Note - the top note is NOT repeated in an ascending+descending scale.
        """
        descending = self.descending if add_descending is None else add_descending
        tonic = MusicUtils.get_note(root)
        pitches = self.pitches(root=tonic, octaves=num_octaves)    # this sets chromatic_pitches
        notes = []
        #
        # create a music21 ConcreteScale
        #
        self._create_music21_scale(tonic, pitches)
        m21Pitches = self.music21Scale.pitches
        for pitch in m21Pitches:
            p = pitch.nameWithOctave.replace("-","b")
            notes.append(p)

        if descending:
            notes_copy = notes.copy()
            notes_copy.reverse()
            notes.extend(notes_copy[1:])

        return notes

    def pitches(self, root:str='C', octaves:int=1)->List[str]:
        """
        Creates and returns the list of pitches for this scale starting with the root note provided. the default root is 'C'. 
        By convention, a pitch does not include an octave designation.
        Arguments:
            root - the default root is 'C' (middle C).
            octaves - the number of octaves to cover, defaults to 1 if not specified.
        """
        tonic = MusicUtils.get_pitch(root)    # strips the octave if there is one, so C3 would return C
        pitches = [tonic]
        self.set_chromatic_pitches()
        ind = self._chromatic_scale.index(tonic)
        formula = self.formula
        for i in formula:
            ind += i
            p = self._chromatic_scale[ind]
            pitches.append(p)
        if octaves > 1:
            # append octaves number of copies to pitches
            # drop the first pitch first so it doesn't repeat the root
            p1 = pitches[1:]
            pitches = pitches + ((octaves-1)*p1)
        return pitches
        
    
    def set_chromatic_pitches(self)->None:
        """ 
            Uses the current Key to select the appropriate set of chromatic notes in self._chromatic_scale.
        """
        accidental = self.key.accidental    # "sharp", "flat"
        accidental_preference = 'b' if accidental=="flat" else "#"
        if('#' == accidental_preference or 'sharp' == accidental_preference):
            self._chromatic_scale = Scale.notes_.get_chromatic_sharp_pitches()
        elif('b' == accidental_preference  or 'flat' == accidental_preference):
            self._chromatic_scale = Scale.notes_.get_chromatic_flat_pitches()
        else:
            self._chromatic_scale = Scale.notes_.get_chromatic_mixed_pitches()
        return 
    
    def get_key_root(self)->str:
        root = self.key.tonic
        return root
    
    def __str__(self):
        root = self.get_key_root()
        return str(self.notes(root))
    
    def __repr__(self):
        return self.scale_data
    
    def to_string(self, root:str)->str:
        root = self.get_key_root()
        return str(self.notes(root))
    
    def to_JSON(self)->dict:
        return self.scale_data
    
    def create_part(self, notes:List[note.Note], transpose_octaves:int)->stream.Part:
        """Create a new Part given a list of Note and number of octaves higher or lower.
            Arguments:
                notes - a List of music21 note.Note. Note the notes must have an octave designation like 'C4'
                transpose_octaves - an int between -2 and 2 inclusive.
            Returns:
                stream.Part consisting of the notes transposed the number of octaves specified.
            TODO
        """
        part_stream = stream.Part()
        semitones = 12 * transpose_octaves
        return part_stream
    
    def chordifyIntervals(self, intervals:Union[List[int], List[str]], root:str="C4", num_octaves:int=1 )->List[chord.Chord]:
        """Chordify the scale using arbitrary intervals, instead of alternating notes.
            Interval list can be specified as a list of integers or strings.
            If a list of int, each is a number of semitones from the previous note, starting with the root, 
            for example [4, 3, 3] with a starting with "C" works out to ["C", "E", "G", "Bb"] as a Chord.
            If a List of str, each entry is an interval name. For example ["M3", "m3", "m3"] is the same chord as the above.
            Valid interval names are 2 characters, the first specifying the quality: M, m, d, a for major, minor, diminished, augmented.
            The second is an integer specifying the size which is a number from 2 to 7.
        """
        chord_size = len(intervals)
        chordList:List[chord.Chord] = list()
        if chord_size==0 or chord_size>self._size:
            raise TypeError("Invalid chord size. Valid range is 1 up to the length of the scale.")
        
        return None
    
    def chordify(self, root="C4",  num_octaves:int=1, chord_size:int=3)->List[chord.Chord]:
        """Create chords for this scale. A chord is built for each scale degree
            by taking alternating notes. The root is the first note of the scale in octave 4.
            Arguments:
                chord_size = the number of notes in each chord. Valid range is 2 (thirds),
                    3 (triads), up to the length of the scale.
                    For example, for a 7-note scale like C-Major, the chord could have up to 7 notes:
                    C E G B D F A (which is a major 13th chord).
                    A 5-note scale, like pentatonic minor (C,D,E,G,A for example) could have up to 5 notes.
                num_octaves - the octave span
            Returns:
                A List[chord.Chord] (music21 chords)
            Raises a TypeError if the chord_size is invalid
        """
        chordList:List[chord.Chord] = list()
        if chord_size<=1 or chord_size>self._size:
            raise TypeError("Invalid chord size. Valid range is 2 up to the length of the scale.")
        #
        # ALgorithm- duplicate the scale if needed. Then for each scale degree, up to an including
        # the size of the scale, create a chord consisting of alternating notes.
        # Chordify ascending first, then add descending if needed.
        #
        scale_size = self._size
        scale_notes = self.notes(root=root, num_octaves=num_octaves+1, add_descending=False)    # the scale notes over a n-octave span
        for root_ind in range(0, num_octaves*scale_size+1):
            chord_notes = list()
            for i in range(chord_size):
                chord_ind = root_ind + 2*i
                chord_notes.append(scale_notes[chord_ind])
            chordList.append(chord.Chord(chord_notes))
            
        return chordList
    
    def _createPartStream(self, root:str, octaves, notes:List[str], note_duration:str, 
             instrument_name:str, second_part_transpose:int, 
             metronome_mark:(int,str), time_signature:str, show_chords:int, add_descending:bool)->stream.Part:
        """Create a stream.Part from the arguments provided.
            Arguments;
            Returns: stream.Part ready to insert into a stream.Score
            NOTE - chord durations are always a quarter note.
        """
        part_instrument,transpose_interval = GeneralUtils.get_instrument(instrument_name)

        part_tempo = tempo.MetronomeMark(number=metronome_mark[0], referent=note.Note(type=metronome_mark[1]))
        notes_per_measure = Notes.notes_per_measure(time_signature, note_duration)
        print(f"notes/measure: {notes_per_measure}")
        
        timeSignature = meter.TimeSignature(time_signature)
        part_clef = MusicUtils.getClef(root, octaves)
        part_stream = stream.Part()
        part_stream.insert(0, metadata.Metadata())
        part_stream.metadata.title = self.name
        part_stream.insert(part_clef)
        #music21Key = self.get_music21_key(self.key, transpose_interval)
        part_stream.insert(self.get_music21_key(transpose_interval))
        part_stream.insert(timeSignature)
        part_stream.insert(part_tempo)
        part_stream.insert(0, part_instrument)
   
        notes_ = self.notes(root=root, num_octaves=octaves) if notes is None else notes
        tn = len(notes_)    # the total number of notes in this scale
        num_measures = int(tn//notes_per_measure)     # number of complete measures
        left_over = int(tn - notes_per_measure*(num_measures))    # the number of notes in the final measure
        note_values = Scale.notes_.get_note_values()
        quarterLength = 4 / note_values[note_duration]     # note_duration expressed as quarter_length
        
        note_count = 0
        part_notes = list()
        for anote in notes_:
            if note_count == tn - 1 and left_over > 0:    # is this the last note? If so, adjust duration to fill the measure
                ql = quarterLength * (notes_per_measure - left_over + 1)
                n = note.Note(anote, quarterLength=ql)
                part_stream.append(n)
                part_notes.append(n)
            else:
                n = note.Note(anote, type=note_duration)
                if transpose_interval.semitones > 0:
                    n_transpose = n.transpose(transpose_interval)
                    part_stream.append(n_transpose)
                    part_notes.append(n_transpose)
                else:
                    part_stream.append(n)
                    part_notes.append(n)
            note_count += 1
            
        if show_chords >= 2:
            chord_list = self.chordify(root=root, num_octaves=octaves, chord_size=show_chords)
            if add_descending:
                for i in range(len(chord_list)-2, -1, -1):
                    c=chord.Chord(chord_list[i].pitches)
                    chord_list.append(c)
            for i in range(len(chord_list)):
                c = chord_list[i]
                c.quarterLength = 1.0   # part_notes[i].quarterLength
                print(c)
                part_stream.append(c)
                
        return part_stream
    
    def show(self, format_:str, root="C4", octaves=1, notes:List[str]=None, note_duration="quarter", 
             instrument_name="Piano", second_part_transpose:int=0, 
             metronome_mark:(int,str)=(120,"quarter"), time_signature:str="4/4", show_chords:int=0, add_descending:bool=False):
        """ Display this scale in a specified format.
            Arguments:
                format_ - valid choices are: "pitches", "notes", "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf"
                root - the root note, default is middle-C
                octaves - the number of octaves to cover, default is 1.
                notes - a List[str] of notes. This is shown if present, and the root and octaves args are ignored.
                note_duration - note duration. Default is "quarter". Valid values are "whole","half","quarter","eighth","16th","32nd","64th"
                instrument_name - the instrument used to voice the scale. Valid instrument are in the instruments.json resource file.
                    The default instrument name is "Piano". @see instruments.py.
                second_part_transpose - an int between -2 and 2 inclusively. If non-zero then add a second part
                    transposing the original scale by that number of octaves. This only applies to music21 and lily formats.
                    Both parts are music21 Part instances.   TODO.
                metronome_mark - a (number,referent) duple that sets the tempo. number is the beats per minute; referent is the note duration that gets the beat.
                    Default value is (100, "quarter"). This also appears in the score display.
                time_signature - as a string, for example "4/4" or "12/4". Beats per measure (the top number) must be in range(1,17).
                    The note value that gets the beat must be a power of 2: [1,2,4,8,16]
                show_chords - if >=2, chordify the scale with show_chords number of notes in each chord.
                
            Raises: a TypeError if the instrument or time signature is invalid.
                
            This is dependent on installing and configuring the music21 package (pip install music21)
            Also MuseScore must be installed. The latest version is MuseScore4.
            Configuring music21 will the the path to MuseScore in the music21 environment (music21-settings.xml)
            By default, notes displayed in musicxml are quarter notes, or type="quarter".

        """
        if format_ == "notes":
            print(self.notes(root, num_octaves=octaves))
            return
        elif format_ == "pitches":
            print(self.pitches(root, octaves))
            return
        scaleScore = stream.Score()
        scaleScore.insert(0, metadata.Metadata())
        scaleScore.metadata.title = self.name
        
        partTwoStream = None
        
        partOneStream= self._createPartStream(root, octaves, notes, note_duration, instrument_name, 
                                                   second_part_transpose, metronome_mark, time_signature, show_chords, add_descending)
        if second_part_transpose != 0:
            # add another par with the root the number of octaves higher or lower than the specified root
            semitones = second_part_transpose * 12
            part_root = MusicUtils.get_music21_note(root, semitones).nameWithOctave
            partTwoStream = self._createPartStream(part_root, octaves, None, note_duration, instrument_name, 
                                                   second_part_transpose, metronome_mark, time_signature, show_chords, add_descending)
            
        scaleScore.insert(partOneStream)
        if partTwoStream is not None:
            scaleScore.insert(partTwoStream)

        scaleScore.show(fmt=format_)

def main():
    description = dedent("""
    Create and display a scale.
    """)
    keys = Keys()
    key_names = keys.key_names
    # TODO finish this - maybe not needed?
    parser = argparse.ArgumentParser(prog="Scale", description=description)
    parser.add_argument("--name",  help="Scale name", type=str, default="MyScale")
    parser.add_argument("--formula", "-F", help="Create a scale with this formula: a comma-separated list. Overrides name lookup.",
                        type=str, default=None)
    parser.add_argument( "--root", "--tonic", "-R",help="Root pitch, default is 'C'. May also include an octave as in 'D3'", type=str, default="C4")
    parser.add_argument("--key", "-K", 
            help="Optional key signature, for example 'Eb-Major', 'F-Minor'. Default key is 'C-Major'. Used to determine accidentals in the scale and the tonic/root note.",
            choices = key_names, type=str, default="C-Major")
    parser.add_argument("--octaves", "-O", 
            help="Octave range, default is 1 octave", type=int, choices=[1,2,3], default=1)
    parser.add_argument("--descending", "-D", 
            help="Create both ascending and descending versions of the scale over the specified octave range. Default is True",
            action="store_true", default=True)
    parser.add_argument("--duration", help="Duration of the notes. Default is 'quarter'", type=str, choices=["whole","half","quarter","eighth","sixteenth"], default="eighth")
    parser.add_argument("--show", "-S", help="Display a scale in MuseScore, lilypond or as a list",  
            type=str, choices=["pitches", "notes", "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf"], default="notes")
    
    args = parser.parse_args()
    key:Key = keys.key(args.key)
    theScale = None
    if args.formula is not None:
        formula = [int(x) for x in args.formula.split(",")]
        theScale = Scale(args.name, key=key, octaves=args.octaves, descending=args.descending, formula=formula)
    else:
        theScale = Scale(args.name, key=key, octaves=args.octaves, descending=args.descending)
        
    if theScale is not None:
        theScale.show(format_=args.show, root=args.root, octaves=args.octaves, note_duration=args.duration, add_descending=args.descending)

if __name__ == '__main__':
    main()

        
        
        