# ------------------------------------------------------------------------------
# Name:          scale.py
# Purpose:       Encapsulate a musical scale.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2026 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from typing import List, Dict
from itertools import accumulate
from functools import cached_property
import operator, itertools
from music21 import stream, note, pitch, scale
from music.key import Key

class Notes(object):
    
    # chromatic pitches given over a 4-octave range
    SHARP_PITCHES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    FLAT_PITCHES =  ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
    MIXED_PITCHES = ['C','C#','D','Eb','E','F','F#','G','G#','A','Bb','B']
    CHROMATIC_SHARP_PITCHES = 4 * SHARP_PITCHES
    CHROMATIC_FLAT_PITCHES =  4 * FLAT_PITCHES
    CHROMATIC_MIXED_PITCHES = 4 * MIXED_PITCHES
    NATURAL_PITCHES = ["C","D","E","F","G","A","B"]
    
    def __init__(self, start_octave=0, num_octaves=8):
        self._num_octaves = num_octaves
        self._start_octave = start_octave
    
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
        The sum of the intervals in a given formula MUST equal 12.
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
        
    def __init__(self, scale_data:dict, key:Key=None, octaves:int=1, descending:bool=False):
        """
        Create a Scale from a dictionary
        Arguments:
            scale_data a dict representing a single scale having the keys described above
                for example: { "name" : "Major" , "groups" : [ "major", "diatonic", "common"] , "formula" : [2,2,1,2,2,2,1] , "size" : 7}
                scale_data argument is mandatory.
            key - optional Key object. Defaults to C-Major if not provided.
                The Key is used to determine the accidental choice. 
                Also the root note of the scale is the tonic note of the key.
            octaves - the number of octaves to cover. Range is 1 to 4, default is 1.
            descending - if True create the scale in descending order. Default is False
        Note a music21.scale.ConcreteScale is also created as needed.
        """
        self._key = Key(key_date=Scale.DEFAULT_KEY) if key is None else key
        self.octaves = octaves
        self.descending = descending
        self.scale_data = scale_data
        assert(len(scale_data)>0)
        self.scale = scale_data
        self._name = self.scale.get('name', "MY_SCALE")
        self._formula = self.scale.get('formula', [])
        self._size = self.scale.get("size", 0)
        self._groups = self.scale.get("groups", [])
        self._alternate_names = self.scale.get("alternateNames", [])
        self._music21Scale = None    # music21.scale.ConcreteScale

    @staticmethod
    def has_octave(note):
        return len(note) > 0 and note[len(note)-1].isdigit()

    @staticmethod
    def get_octave(note:str, default_octave=-1)->int:
        """ Gets the octave designation of a given note.
            If the note is in scientific notation (as in C4 or Bb2), it returns the octave as an int.
            Otherwise it returns the default_octave argument, which defaults to -1.
        """
        if(Scale.has_octave(note)):
            return  note[-1:]
        else:
            return default_octave

    @staticmethod
    def get_octaves(*notes)->List[int]:
        """ Gets the octave designation for a list of notes.
            Arguments:
                notes - variable number of str arguments.
            Returns a List[int] of the octave values of those notes.
                The octave value for a note that does not have an octave is -1.
        """
        return[Scale.get_octave(note) for note in notes]

    @staticmethod
    def get_pitch(note)->str:
        """Strips the octave designation of a given note  """
        return note[:-1] if Scale.has_octave(note) else note

    @staticmethod
    def get_note(note:str, default_octave:int=4)->str:
        """Adds an octave designation to a given note, default octave is 4
            but can be set to any int >=-1.
            Returns the input note if it already has an octave.
        """
        return note if Scale.has_octave(note) else  f"{note}{default_octave}"
    
    @staticmethod
    def getNote(note:str)->(str,int):
        """ Adds an octave designation to a given note, default octave is 4
            but can be set to any int >=-1.
            Returns pitch,octave as a str,int pair.
        """
        pitch = Scale.get_pitch(note)
        octave = int(Scale.get_octave(note, default_octave=4))
        return pitch,octave
    
    @staticmethod
    def _get_chromatic_pitches(num_octaves=2, start_octave=-1)->Dict[str,List[str]]:
        """ Returns a list of chromatic pitches in ascending order over the number of octaves indicated.
            Arguments: 
                num_octaves - the octave range, default value is 2.
                start_octave - optional argument to produce notes in scientific notation (pitch+octave as in C4).
                    Default value is -1, an invalid octave designation.
        """
        if start_octave < 0:
            cpf = num_octaves * Notes.FLAT_PITCHES       # 12 pitches x #octaves
            cps = num_octaves * Notes.SHARP_PITCHES
            cpm = num_octaves * Notes.MIXED_PITCHES
            cp = {"flat":cpf, "sharp":cps, "mixed":cpm}
        else:
            cpf = []
            cps = []
            cpm = []
            for octave in range(start_octave, start_octave+num_octaves):
                for pitch in Notes.FLAT_PITCHES:
                    cpf.append(f"{pitch}{octave}")
                for pitch in Notes.SHARP_PITCHES:
                    cps.append(f"{pitch}{octave}")
                for pitch in Notes.MIXED_PITCHES:
                    cpm.append(f"{pitch}{octave}")
            cp = {"flat":cpf, "sharp":cps, "mixed":cpm}
        return cp
    
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
            chromatic_pitches = Notes.CHROMATIC_FLAT_PITCHES if key.accidental.startswith("flat") else Notes.CHROMATIC_SHARP_PITCHES
        else:
            chromatic_pitches = Notes.CHROMATIC_SHARP_PITCHES if key.accidental.startswith("flat") else Notes.CHROMATIC_FLAT_PITCHES
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

        if "b" in  root_pitch or accidental == "b":
            ind = Notes.CHROMATIC_FLAT_PITCHES.index(root_pitch)
            pitches = [Notes.CHROMATIC_FLAT_PITCHES[x+ind] for x in pitch_set]
        elif "#" in root_pitch or accidental == "#" or root_pitch[0] in "GDAEB":    # there's # in the root_pitch or it's the root of a sharp key
            ind = Notes.CHROMATIC_SHARP_PITCHES.index(root_pitch.upper())
            pitches = [Notes.CHROMATIC_SHARP_PITCHES[x+ind] for x in pitch_set]
        else:
            ind = Notes.CHROMATIC_FLAT_PITCHES.index(root_pitch)
            pitches = [Notes.CHROMATIC_FLAT_PITCHES[x+ind] for x in pitch_set]
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
    
    def _compare_pitches(self, pitch1, pitch2, root)->int:
        """ Compare 2 notes without octaves relative to a given root. """
        accidental1 = "#"
        return 0
        
    
    def compare_notes(self, note1:str, note2:str, root:str=None)->int:
        """ Compare 2 notes relative to a chromatic scale starting on a given root pitch
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
            Throws a TypeError if the arguments are inconsistent or don't represent notes.
            
            TODO finish this and make static
        """
        result = 0
        root = "C" if root is None else root
        octaves = Scale.has_octave(note1) + Scale.has_octave(note2)  # 0==no note octaves, 2==both notes have octaves, 1==one does, one doesn't, invalid
        if octaves == 1:    # they must all have octave or not
            raise(TypeError("All arguments must include an octave or not"))
        if octaves == 2:
            # a root note is not needed is both notes are is scientific notation (have octaves)
            o1,o2 = Scale.get_octaves(note1,note2)
            if o1 == o2:   # same octave so compare notes 
                p1 = Scale.get_pitch(note1)
                p2 = Scale.get_pitch(note2)
            else:
                result = -1 if o1 < o2 else 1
        if octaves == 0:   # compare 2 pitches relative to a chromatic scale whose starting note is root
            pass
            
        return result
    
    def _create_music21_scale(self, tonic:str, pitches:List[str]):
        """ Create a music21 ConcreteScale from a list of pitches.
            Arguments:
                tonic - the tonic note of the scale as a pitch or note (pitch+octave)
                pitches - a list of pitches as List[str]
            Sets m21Scale property
        """
        m21Pitches = [x.replace("b","-") for x in pitches]
        self._music21Scale = scale.ConcreteScale(tonic=tonic, pitches=m21Pitches)

    def notes(self, root='C4', num_octaves:int=1, accidental_preference:str=None)->List[str]:
        """
        Creates and returns the list of notes for this scale starting with the root provided. 
        Arguments:
        root - the default root is 'C4' (middle C).
            If the root provided lacks an octave, 4 is assumed.
            By convention, notes are expressed in scientific music notation which includes an octave designation starting at 0
            For example, the range of a Piano is A0 to C8.
            Octaves are from C to B, so the pitch following B4 is C5.
            In general the accidental (# or b) used is determined first by the root note. If the root doesn't have an accidental,
            the accidental_preference is used. If a preference is not provided a # is the default.
        accidental_preference: 'sharp', '#', 'flat', 'b', 'mixed', '#b' or 'key'
        
        ['C', 'Eb', 'F', 'Ab', 'Bb', 'C', 'Eb', 'F', 'Ab', 'Bb', 'C']
        """
        _ap = self.get_accidental_preference(root, accidental_preference)
        tonic = Scale.get_note(root)
        pitches = self.pitches(root=tonic, octaves=num_octaves, accidental_preference=accidental_preference)
        notes = []
        #
        # create a music21 ConcreteScale
        #
        self._create_music21_scale(tonic, pitches)
        m21Pitches = self.music21Scale.pitches
        for pitch in m21Pitches:
            p = pitch.nameWithOctave.replace("-","b")
            notes.append(p)

        if self.descending:
            notes.reverse()

        return notes

    def pitches(self, root:str='C', octaves:int=1, accidental_preference:str=None)->List[str]:
        """
        Creates and returns the list of pitches for this scale starting with the root note provided. the default root is 'C'. 
        By convention, a pitch does not include an octave designation.
        Arguments:
            root - the default root is 'C' (middle C).
            accidental_preference: 'sharp', '#', 'flat', 'b', 'mixed', '#b' or 'key'
            octaves - the number of octaves to cover, defaults to 1 if not specified.
        """
        tonic = Scale.get_pitch(root)    # strips the octave if there is one, so C3 would return C
        pitches = [tonic]
        _ap = self.get_accidental_preference(root, accidental_preference)
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
    
    def get_accidental_preference(self, root, accidental_preference:str=None)->List[str]:
        """ 
            Arguments:
                root - a note or pitch string
                accidental_preference - flat, sharp, mixed, or an accidental symbol:
                "-" or "b" for flat, "#" for sharp. "-" is the music21 symbol for flat
        """
        accidental = self.key.accidental    # "sharp", "flat" or "mixed"
        if accidental_preference is None:
            if(accidental == "sharp" or "#" in root):
                ap = '#'
                self._chromatic_scale=Notes.CHROMATIC_SHARP_PITCHES
            elif(accidental == "flat" or accidental == "-"  or "b" in root):
                ap = 'b'
                self._chromatic_scale=Notes.CHROMATIC_FLAT_PITCHES
            else:
                ap = '#b'
                self._chromatic_scale=Notes.CHROMATIC_MIXED_PITCHES
        else:
            if('#' == accidental_preference or 'sharp' == accidental_preference):
                ap = '#'
                self._chromatic_scale=Notes.CHROMATIC_SHARP_PITCHES
            elif('b' == accidental_preference  or "-" ==  accidental_preference or 'flat' == accidental_preference):
                ap = 'b'
                self._chromatic_scale=Notes.CHROMATIC_FLAT_PITCHES
            elif('#b' == accidental_preference or 'mixed' == accidental_preference):
                ap = '#b'
                self._chromatic_scale=Notes.CHROMATIC_MIXED_PITCHES
            else:
                ap = '#b'
                self._chromatic_scale=Notes.CHROMATIC_MIXED_PITCHES
        return ap
    
    def __str__(self):
        return str(self.notes(root="C", accidental_preference='mixed'))
    
    def __repr__(self):
        return self.scale_data
    
    def to_string(self, root:str)->str:
        return str(self.notes(root, accidental_preference='mixed'))
    
    def to_JSON(self)->dict:
        return self.scale_data
    
    def show(self, format_:str, root="C4", octaves=1, notes:List[str]=None):
        """ Display this scale in a specified format.
            Arguments:
                format_ - one of "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf", "pitches", "notes"
                root - the root note, default is middle-C
                octaves - the number of octaves to cover, default is 1.
                notes - a List[str] of notes. This is shown if present, and the root and octaves args are ignored.
                
            This is dependent on installing and configuring the music21 package (pip install music21)
            Also MuseScore must be installed. The latest version is MuseScore4.
            Configuring music21 will the the path to MuseScore in the music21 environment (music21-settings.xml)
        """
        note_stream = stream.Stream()
        notes_ = self.notes(root=root, octaves=octaves) if notes is None else notes
        for anote in notes_:
            n = note.Note(anote)
            note_stream.append(n)
        note_stream.show(fmt=format_)

if __name__ == '__main__':
    print(Scale.__doc__)

        
        
        