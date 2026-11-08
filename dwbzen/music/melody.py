'''
Created on Oct 22, 2026

@author: don_bacon
'''

from music.musicUtils import MusicUtils
from music21 import stream, note, pitch, duration, Music21Object, tie
from music21 import metadata, instrument, tempo, meter, interval
from music.keys import Keys
from music.key import  Key
from music.generalUtils import GeneralUtils
from music.notes import Notes
from music.scale import Scale
from music.scales import Scales
import argparse
from typing import List
from dataclasses import dataclass, field
from enum import Enum
import random

class DurationType(Enum):
    WHOLE = "whole"
    HALF = "half"
    QUARTER = "quarter"
    EIGHTH = "eighth"
    SIXTEENTH = "16th"
    THIRTY_SECOND = "32nd"
    SIXTY_FOURTH = "64th"

class StaffObjectType(Enum):
    NOTE  = "note"
    CHORD = "chord"
    REST  = "rest"

@dataclass
class StaffObject:
    staffObjectType:StaffObjectType = field(default=StaffObjectType.NOTE)    # note, rest, or chord
    pitch:str = field(default=None)
    octave:int = field(init=False)
    isRest:bool = field(init=False)    # objectType is "rest"
    
    durationType:DurationType = field(default=None)
    quarterLength:float = field(default=None)
    dots:int = field(default=0)

    # noteDuration set from durationType or quarterLength and dots
    # applies to any staffObjectType
    noteDuration:duration.Duration = field(init=False)
    
    # anything that can go into a stream: music21 Note, Pitch, Chord, Clef, Rest, etc.
    music21Object:Music21Object = field(default=None)
    tieType:str = field(default=None)    # "start ", "stop", None

    def __post_init__(self):
        self.isRest = (self.staffObjectType == StaffObjectType.REST)
        hasoctave = self.pitch is not None and len(self.pitch) > 1 and self.pitch[len(self.pitch)-1].isdigit()
        self.octave = int(self.pitch[-1:]) if hasoctave else 4
        if not hasoctave:
            self.pitch = f"{self.pitch}{self.octave}"
        if self.durationType is not None:
            self.noteDuration = duration.Duration(type=self.durationType.value, dots=self.dots)
            self.quarterLength = self.noteDuration.quarterLength
        elif self.quarterLength is not None:
            self.noteDuration = duration.Duration(self.quarterLength, dots=self.dots)
            self.durationType = DurationType(self.noteDuration.type)
        else:
            self.noteDuration = duration.Duration("quarter")
            self.quarterLength = 1.0
        # create the appropriate music21Object
        match self.staffObjectType:
            case StaffObjectType.NOTE:
                self.music21Object = note.Note(nameWithOctave=self.pitch)
                self.music21Object.duration = self.noteDuration
                if self.tieType is not None:
                    self.music21Object.tie = tie.Tie(self.tieType)
            case StaffObjectType.REST:
                self.music21Object = note.Rest()
                self.music21Object.duration = self.noteDuration
            case StaffObjectType.CHORD:    # TODO
                pass    # melody may include chord(s)
            case _: 
                raise TypeError("Invalid staff object type")

    def __str__(self)->str:
        """ The stringified StaffObject is essentially the __repr__()
        """
        if self.isRest:
            return f"{self.music21Object}"
        else:
            if self.tieType is None:
                s = f"{self.music21Object.nameWithOctave}/{self.quarterLength}/{self.dots}" 
            else:
                s =  f"{self.music21Object.nameWithOctave}/{self.quarterLength}/{self.dots}/{self.tieType}"
            return s
    
    def __repr__(self)->str:
        return self.__str__()

    
class Melody(object):
    
    _QUARTER_LENGTHS:List[float] = None
    _DURATION_WEIGHTS:List[int] = None
    
    """ A Melody is a bespoke sequence of notes. Each note has a specified duration
        and may be a rest.
        The API supports tone row operations: inverted, retrograde, inverted-retrograde, and transposition.
    """
    def __init__(self, name:str, key_name:str="C-Major", startNote=None, formula:List[int]=None, 
                 duration:str|DurationType=None, metronome_mark=None, notes:str=None, randomMelody:(str,str,int,bool,float)=None):
        """
        Construct a new Melody.
        Arguments
            name - the name of your Melody. If unspecified, the name defaults to "MyMelody"
            key - optional Key instance. Defaults to C-Major if not provided. The format is <root>-<mode> where mode is "Major" | "Minor"
            
            startNote - must be specified if a formula is also specified.
                An octave designation of 4 is assumed if not present in the note.
            formula - the Melody expressed as a formula (List[int]).
                If a formula is specified, a starting note must also be specified.
            duration - a string specifying the duration such as "quarter", must by a valid DurationType.
                Duration is used when a formula is specified and defaults to "quarter".
                Converted to a DurationType if duration is s a string.
                
            metronome_mark - (int, str) duple specifying the b.p.m and the note value that receives the beat.
            notes - the notes of the melody specified as a comma-separated note values. See parse_note() below for more info.
                Internally, notes are converted to a StaffObject
            random_melody - a (str, str, int, bool) 5-element tupple specifying the range of notes (as start_note, end_note),
                the number of notes, how to sample (True - sample with replacement), and the probability that a rest appears instead of a note
                to use in creating a random melody. For example: ("C4", "F5", 12, True, 0.0)          .
            
            All arguments except name may be omitted, notes may be added with addNote() function.
                
        """
        self.debug = 0    # 2 for more detail
        self._name = "My Melody" if name is None else name
        keys = Keys()
        self._key = keys.key(key_name)
        self._scales = Scales(self._key)
        self._notes = Notes()
        if duration is None:
            self._duration = DurationType.QUARTER
        else:
            self._duration = duration if isinstance(duration, DurationType) else DurationType(duration)
        self._staff_objects:List[StaffObject] = list()
        self._formula = formula
        self._metronome_mark = (100,"quarter") if metronome_mark is None else metronome_mark
        
        if formula is not None:
            self._notes = list()
            self._startNote = "C4" if startNote is None else startNote
            note_list = MusicUtils.get_notes_from_formula(formula, startNote, self._key)    # returns List[note.Note]
            for anote  in note_list:
                self._notes.append(f"{anote.nameWithOctave}/{self._duration.value}/0")    # for example, "C4/quarter/0" where dots == 0
                
        elif randomMelody is not None:    # (str,str,int,bool,float)
            self.random_melody(randomMelody[2], (randomMelody[:2]), randomMelody[3], randomMelody[4])
        else: 
            self._notes = list() if notes is None else notes    # could be empty in which cas notes are added with add_note()
            #
            # Convert the notes to StaffObjects
            #
            for anote in self._notes:
                self._staff_objects.append(self.parse_note(anote))
        
    def parse_note(self, note_spec:str, default_duration=1.0)->StaffObject:
        """
        Argument
            note_str - A note value is specified as pitch/duration/dots/tieType. If a pitch is missing an octave, 4 is assumed.
                A pitch of "0" is used for a rest. Duration may be specified by name ("whole", "half", etc.) OR
                as a quarterLength (float). Either way it is converted to a music21 duration.Duration.
                Example: "C4/eighth", "Eb4/quarter", "0/0.5", "G#4/eighth", "B4/quarter", "C5/0.5"
                "C4/eighth/1" is a dotted eighth note.
                tieType is optional and defaults to None. Valid values are 'start' and 'stop'
            default_duration - as a quarterLength, defaults to 1.0 (quarter note)
        Raises a music21.pitch.PitchException if the pitch is invalid (like "Z#")
        """
        isRest = False
        dots = 0
        assert note_spec is not None
        np = note_spec.split("/")    # (pitch, duration, dots, tieType)
        p = np[0].upper().strip()
        if p=="0":
            isRest = True
            m21note = note.Rest()

        else:
            pitch = MusicUtils.get_note(p, default_octave=4)
            m21note = note.Note(pitch)    # quarter note by default

        #
        tieType = None
        if len(np) == 1:   # assume a quarter note duration, 0 dots
            note_duration = duration.Duration(quarterLength=default_duration)
        if len(np) >= 2:
            dur = np[1]
            if dur.isdigit() or "." in dur:
                note_duration = duration.Duration(quarterLength=float(dur))
            else:
                note_duration = duration.Duration(type=dur)
            if len(np) == 3:
                dots = int(np[2])
            if len(np) == 4:
                tieType = np[3]
        m21note.duration = note_duration
        objectType = StaffObjectType.REST if isRest else StaffObjectType.NOTE
        staffObject = StaffObject(staffObjectType=objectType, pitch=p, durationType=DurationType(note_duration.type), dots=dots, tieType=tieType)
        
        return staffObject
    
    def add_note(self, anote:str)->int:
        staff_object = self.parse_note(anote)
        self._staff_objects.append(staff_object)
        return(len(self._staff_objects))
    
    @property
    def staff_objects(self)->List[StaffObject]:
        return self._staff_objects
    
    @property
    def key(self)->Key:
        return self._key
    
    @property
    def name(self)->str:
        return self._name
    
    @name.setter
    def name(self, newname)->None:
        self._name = newname
    
    @property
    def formula(self)->List[int]:
        return self._formula
    
    def get_notes(self)->List[str]:
        notes = [str(staff_object) for staff_object in self.staff_objects]
        return notes
    
    def get_music21Objects(self)->List[Music21Object]:
        """Each Music21Object is either a Note or a Rest.
        """
        m21Objects = [s.music21Object for s in self ]
        return m21Objects
    
    def __iter__(self):
        return self._staff_objects.__iter__()
    
    @classmethod
    def get_quarter_lengths(cls)->List[float]:
        """ Gets the list of quarter lengths for use as duration.Duration.
            Computed range is [0.25, 0.5, 0.75, 1.0,   1.25, 1.5, 1.75, 2.0,   2.25, 2.5, 2.75, 3.0,   3.25, 3.5, 3.75, 4.0]
        """
        if cls._QUARTER_LENGTHS is None:
            cls._QUARTER_LENGTHS = [x/4 for x in range(1,17)]
        return cls._QUARTER_LENGTHS
    
    @classmethod
    def get_duration_weights(cls)->List[int]:
        """ Gets relative weights for use in random.choices of QUARTER_LENGTHS
            Returns a List[int] of length 16. 
            The most likely is 0.5 which corresponds to an eight note, followed by 16th, quarter, ... up to a whole note
        """
        if cls._DURATION_WEIGHTS is None:  #
            cls._DURATION_WEIGHTS = [5,20,3,10,  2,8,2,6,  0,1,0,1,  0,1,0,1] 
        return cls._DURATION_WEIGHTS
    
    @classmethod
    def get_durations(cls, length:int)->List[duration.Duration]:
        """ Gets a List  of Durations having 'length' elements.
        """
        qlen = Melody.get_quarter_lengths()
        weights = Melody.get_duration_weights()
        quarter_lengths =  random.choices(qlen, weights=weights, k=length)
        durs = [duration.Duration(ql) for ql in quarter_lengths]
        return durs
    
    def _getScaleNotes(self, start_note:str, end_note:str)->List[note.Note]:
        scale_notes:[note.Note] = list()
        key_name = self.key.key_name    # <tonic>-['Major' | 'Minor'], as in "Eb-Major" or "B-Minor"
        scale_name = "Minor" if "Minor" in key_name else "Major"
        theScale = self._scales.get_scale(scale_name, self._key, octaves=1)
        #scale_pitches = theScale.music21Scale.pitches    # List[music21.Pitch]
        notes = theScale.notes(root=start_note, num_octaves=4)    # List[str]
        for anote in notes:
            if self._notes.compare_notes(anote, end_note) <=0:
                scale_notes.append(note.Note(anote))
            else:
                break

        return scale_notes
    
    def random_melody(self, length:int, note_range:(str,str), sample:str, twelve_tone:bool, rest_probabilty:float=0.0)->None:
        """ Create a random melody.
            Arguments:
                length - the melody length to produce (number of notes)
                note_range - sample from the notes in this range. For example ("C4", "C6")
                sample - how to sample the notes in the note_range.
                    True - sample with replacement
                    False - sample without replacement
                    If False, the len of notes in note_range must be <= length of the melody.
                twelve_tone - enable 12-tone note selection
                rest_probability - the probability that a rest can appear in the Melody in place of a note.
                                   Default is 0.0
            Returns:
                None. Initializes self with A List[StaffObject].
            Raises: random.sample() raises a ValueError if Sample larger than population or is negative
            Note that if rest_probability > 0.0, there will be fewer notes than specified by 'length'.
            That's because of the random substitution of a Rest in place of a Note.
            To create a 12-note tone row, set length=12, sample=False, rest_probability to 0.0,
            and note_range to span 12 notes an octave, for example ("Bb3", "B3")
        """
        melody_notes:[note.Note] = list()
        notes_ = self._notes
        anote_start = note_range[0]
        anote_end = note_range[1]
        note_numbers = notes_.get_note_number(anote_start, anote_end)
        start_note_number = note_numbers[anote_start]
        end_note_number = note_numbers[anote_end]
        if twelve_tone:
            sig = self._key.signature    # number of accidentals
            accidental = self._key.accidental    # sharp or flat
            num_sharps = sig if accidental=="sharp" else -sig
            note_list:List[note.Note] = notes_.get_notes(start_note_number, end_note_number, num_sharps=num_sharps)
        else:
            note_list:List[note.Note] = self._getScaleNotes(anote_start, anote_end)
        
        nnotes = len(note_list)
        if (not sample) and nnotes < length:
            raise ValueError("Invalid length for note_range")
        #
        # now select random notes from note_list
        #
        if sample=="choices": # sample with replacement
            melody_notes = random.choices(note_list,k=length)
        elif sample=="sample":      # sample without replacement
            melody_notes = random.sample(note_list, nnotes)
        #
        # create Staff objects
        #
        durations = Melody.get_durations(length)    # List[duration.Duration]
        index = 0
        nnotes = 0
        for anote in melody_notes:
            note_duration = durations[index]
            index += 1
            isRest = random.random() <= rest_probabilty 
            if isRest:
                objectType = StaffObjectType.REST 
            else:
                objectType = StaffObjectType.NOTE
                nnotes += 1
            p = anote.pitch.nameWithOctave
            if self.debug > 0:
                print(f"pitch: {p}  {objectType} {note_duration}, {note_duration.dots}")
            if note_duration.isComplex:   # requires multiple, tied notes
                durComponents = note_duration.components    # DurationTupple
                # add each component separately and tie them
                # there will never be more than 2
                dur = durComponents[0]
                sobj1 = StaffObject(staffObjectType=objectType, pitch=p, quarterLength=dur.quarterLength, dots=dur.dots, tieType="start")
                self._staff_objects.append(sobj1)
                dur = durComponents[1]
                sobj2 = StaffObject(staffObjectType=objectType, pitch=p, quarterLength=dur.quarterLength, dots=dur.dots, tieType="stop")
                self._staff_objects.append(sobj2)
                if self.debug > 0:
                    print(f"  staffObjects:  {sobj1}  {sobj2}")              
            else:
                staffObject = StaffObject(staffObjectType=objectType, pitch=p, quarterLength=note_duration.quarterLength, dots=note_duration.dots)
                if self.debug > 0:
                    print(f"  staffObject:  {staffObject}")
                self._staff_objects.append(staffObject)
        
        #print(f"num of notes: {nnotes}\nnotes: {melody_notes}")
    
    def inverted(self, inPlace=False):
        """ Create an inversion of this Melody.
        """
        raise NotImplementedError("inverted")
    
    def retrograde(self, inPlace=False):
        raise NotImplementedError("retrograde")
    
    def retrograde_inversion(self, inPlace=False):
        raise NotImplementedError("retrograde_inversion")
    
    def tone_row(self, rest_probability=0.0, inPlace=False):
        raise NotImplementedError("tone_row")


    def show(self, fmt:str, instrument_name="Piano", metronome_mark:(int,str)=(120,"quarter"), time_signature:str="4/4")->str|None:
        """ Display this scale in a specified format.
            Arguments:
                format_ - valid choices are: "pitches", "notes", "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf"
                notes - a List[Music21Object] each could be a Note or a Rest.
                instrument_name - the instrument used to voice the scale. Valid instrument are in the instruments.json resource file.
                    The default instrument name is "Piano". @see instruments.py.
                metronome_mark - a (number,referent) duple that sets the tempo. number is the beats per minute; referent is the note duration that gets the beat.
                    Default value is (100, "quarter"). This also appears in the score display.
                time_signature - as a string, for example "4/4" or "12/4". Beats per measure (the top number) must be in range(1,17).
                    The note value that gets the beat must be a power of 2: [1,2,4,8,16]
                
            Raises: a TypeError if the instrument or time signature is invalid.
                
            This is dependent on installing and configuring the music21 package (pip install music21)
            Also MuseScore must be installed. The latest version is MuseScore4.
            Configuring music21 will the the path to MuseScore in the music21 environment (music21-settings.xml)
            By default, notes displayed in musicxml are quarter notes, or type="quarter".

        """
        if fmt == "notes":
            out_str = ""
            for sobj in self._staff_objects:
                s = f"{sobj.music21Object}" if sobj.isRest else f"{sobj.music21Object.nameWithOctave}"
                print(s)
                out_str = f"{out_str} {s}"
            return out_str
        elif fmt == "pitches":
            s =  [f"{sobj.music21Object} " for sobj in self._staff_objects]
            print(s)
            return s
        #
        sobj = self.staff_objects[0]
        first_note = sobj.music21Object.nameWithOctave    # used to determine the Clef
        
        scaleScore = stream.Score()
        scaleScore.insert(0, metadata.Metadata())
        scaleScore.metadata.title = self.name
        part_instrument,transpose_interval = GeneralUtils.get_instrument(instrument_name)
        part_tempo = tempo.MetronomeMark(number=metronome_mark[0], referent=note.Note(type=metronome_mark[1]))
        
        timeSignature = meter.TimeSignature(time_signature)
        part_clef = MusicUtils.getClef(first_note)
        part_stream = stream.Part()
        part_stream.insert(0, metadata.Metadata())
        part_stream.metadata.title = self.name
        part_stream.insert(part_clef)
        
        part_stream.insert(MusicUtils.get_music21_key(self._key, transpose_interval))
        part_stream.insert(timeSignature)
        part_stream.insert(part_tempo)
        part_stream.insert(0, part_instrument)
        for staff_object in self.staff_objects:
            sobj = staff_object.music21Object
            part_stream.append(sobj)
            # TODO account for transpose_interval > 0
        scaleScore.insert(part_stream)
        scaleScore.show(fmt=fmt)
        

def main():
    keys = Keys()
    key_names = keys.key_names
        
    description = "Construct and view a Melody"
    parser = argparse.ArgumentParser(prog="Melody", description=description)
    parser.add_argument("--name", help="Melody name", type=str, default="MyMelody")
    parser.add_argument("--notes", help="String of comma-separated notes", type=str, default="C4/quarter")
    #
    # random melody arguments
    #
    parser.add_argument("--random", "-R",
                        help="Create a random melody of a specified length from a given range of notes. Format is: 'start_note/end_note/length'",
                        type=str, default=None)
    parser.add_argument("--rest", help="Probability that a rest will appear in a random melody Default is 0.0 (no rests)",
                        type=float, default=0.0)
    parser.add_argument("--sample", "-S", help="How to sample notes: 'choices': sample with replacement, 'sample': without replacement ", type=str,
                        choices=["sample","choices"], default="choices")
    #
    # format and playback
    #
    parser.add_argument("--instrument", help="The instrument name, default is 'Piano'", type=str, default="Piano")
    parser.add_argument("--key", "-K", 
            help="Optional key signature, for example 'Eb-Major', 'F-Minor'. Default key is 'C-Major'. Used to determine accidentals in the scale and the tonic/root note.",
            choices = key_names, type=str, default="C-Major")
    parser.add_argument("--fmt", "-F", help="Display the Melody in MuseScore, lilypond or as a list of pitches or notes",  
        type=str, choices=["pitches", "notes", "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf"], default="notes")
    #
    # additional parts (TODO)
    #
    parser.add_argument("--harmonize", "-H", help="Harmonize the main melody with a second melody part", type=str, default=None)
    parser.add_argument("--chords", "-C", help="Add a second part consisting of chords.", type=str, default=None)
    
    args = parser.parse_args()
    key_name = args.key
    
    if args.random is not None:
        rand_args = args.random.split("/")
        if len(rand_args) != 3:
            print("Format is: 'start_note/end_note/length'")
            return
        
        start_note = MusicUtils.get_note(rand_args[0])
        end_note = MusicUtils.get_note(rand_args[1])
        length = int(rand_args[2])
        
        rest_probabilty=args.rest
        melody = Melody(name=args.name,  key_name=key_name, randomMelody=(start_note, end_note, length, args.sample, rest_probabilty))

        melody.show(fmt=args.fmt, instrument_name=args.instrument)
        
    else:
        melody = Melody(args.name)
        note_list = args.notes.split(",")
        for anote in note_list:
            melody.add_note(anote)
        
        melody.show(fmt=args.fmt, instrument_name=args.instrument)
        
if __name__ == '__main__':
    main()

        
        
        
        