# ------------------------------------------------------------------------------
# Name:          instruments.py
# Purpose:       Instrument utilities.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from music21 import instrument, Music21Object
from music21 import note, clef, interval

import pandas as pd
import importlib

class Instruments(object):
    """Encapsulates instrument information for the instruments supported by this framework:
       * music21 module
       * associated music21 class and class instance
       * range of the instrument - (low,high) as pitches
       * pitchRange - (low,high) as pitch pitch space attribute
       * Clef to use
       * transposeDiatonic
       * transposeChromatic
       * transposeText

    Instrument information maintained in resources/music/instruments.json
    Clef information in resources/music/clefs.json

    """
    
    instrument_names=[ 'Alto', 'Bass', 'Bassoon', 'Clarinet', 'Flute', 'Harpsichord', 'Koto', 'Oboe', 'Piano', 'PianoLH', 'PianoRH', 'Soprano', 'Tenor']
    clef_names=['Soprano', 'Alto', 'Tenor', 'Bass', 'Treble', 'Treble8va', 'Treble8vb', 'Bass8va', 'Bass8vb', 'C', 'F', 'G']
    
    def __init__(self, verbose=0, resource_folder ="/Compile/dwbzen/resources/music"):
        self.resource_folder = resource_folder
        self.verbose = verbose
        self.__create_instrument_classes()
        self.__create_clef_classes()

    @staticmethod
    def __create_instance(row:pd.Series) -> Music21Object:
        """Create an instance of a given class.
        
            Args:
                row - a pd.Series that has ''module' and 'class' members
            Returns:
                a module.class instance
        
        """
        module = row['module']
        class_name = row['class']
        my_module = importlib.import_module(module)
        MyClass = getattr(my_module, class_name)
        instance = MyClass()
        return instance
    
    @staticmethod
    def __define_pitch_range(row:pd.Series):
        notes = row['range'].split(",")
        nlow = note.Note(notes[0])
        nhigh = note.Note(notes[1])
        rlow = int(nlow.pitch.ps)
        rhigh = int(nhigh.pitch.ps)
        return [rlow,rhigh]
    
    def __create_instrument_classes(self):
        self.instruments_pd = pd.read_json(self.resource_folder + "/instruments.json", orient="index")
        self.instruments_pd['instance'] = [Instruments.__create_instance(row[1]) for row in self.instruments_pd.iterrows()]
        self.instruments_pd['range_ps'] = [Instruments.__define_pitch_range(row[1]) for row in self.instruments_pd.iterrows()]
        self.instruments_pd.fillna(value={'transposeDiatonic':0}, inplace=True)
        self.instruments_pd.fillna(value={'transposeChromatic':0}, inplace=True)
        self.instruments_pd.fillna(value={'transposeText':'Non-transposing'}, inplace=True)
    
    def __create_clef_classes(self):
        self.clefs_pd = pd.read_json(self.resource_folder + "/clefs.json", orient="index")
        self.clefs_pd['instance'] = [Instruments.__create_instance(row[1]) for row in self.clefs_pd.iterrows()]

    def get_clef(self, clef_name) -> clef.Clef:
        instance = None
        if clef_name in self.clefs_pd.index:
            instance = self.clefs_pd.loc[clef_name]['instance']
        return instance
    
    def get_instrument_clef(self, instrument_name) -> clef.Clef:
        instance = None
        if instrument_name in self.instruments_pd.index:
            clef_name = self.instruments_pd.loc[instrument_name]['clef']
            instance = self.get_clef(clef_name)
        return instance
    
    def get_instrument(self, instrument_name) -> instrument.Instrument:
        instance = None
        if instrument_name in self.instruments_pd.index:
            instance = self.instruments_pd.loc[instrument_name]['instance']
        return instance
    
    def is_in_range(self, instrument_name:str, note:note.Note) -> bool:
        """Return True if a Note is in the rage of a given Instrument, False otherwise
        
        """
        noteps = note.pitch.ps
        rng = self.instruments_pd.loc[instrument_name]['range_ps']
        inrange = (noteps >= rng[0] and noteps <= rng[1])
        return inrange
    
    def check_range(self, instrument_name:str, note:note.Note) -> int:
        """Returns the number of steps a Note is for a given Instrument, 0 otherwise.
        
            Args:
                instrument_name - the name of a supported Instrument
                note - the Note to test
            Returns:
                0 if in range
                if not in range, the #steps (semitones) the note is beyond the range.
                If <0, the Note is below by that number of steps
                If >0 the note is above by that number of steps
            Note:
                If note.octave is None, music21 assumes octave 4 for all notes.
                So 'C' is treated as 'C4' with a pitch.ps value of 60.
                and 'B' is treated as 'B4' with a pitch.ps value of 71.
        
        """
        steps_out_of_range = 0
        noteps = note.pitch.ps
        rng = self.instruments_pd.loc[instrument_name]['range_ps']
        if noteps < rng[0]:
            steps_out_of_range = noteps - rng[0]
        elif noteps > rng[1]:
            steps_out_of_range = noteps - rng[1]
        return int(steps_out_of_range)
    
    def adjust_to_range(self, instrument_name:str, anote:note.Note, inPlace=False) -> note.Note:
        """Adjust the pitch of a Note if out of range.
            If below the instrument range, the note is transposed up by the number of octaves needed to be back in range.
            If above the instrument range, the note is transposed down by the number of octaves needed to be back in range.
        
            Args:
                instrument_name - the name of a supported Instrument
                anote - the Note to test and possibly transpose
                inPlace - if True anote is transposed in place, else a new Note is returned and the original unchanged.
            Returns:
                a new note that is in range. If inPlace is True, the note provided is transposed in place.
                The original note is returned unchanged if already in range.
        
        """
        steps_out_of_range = self.check_range(instrument_name, anote)
        #
        # if the note is out of range for this part (instrument)
        # transpose up an octave is below the range, down an octave if above
        if steps_out_of_range != 0:
            if self.verbose > 1:
                print(f"newnote: {anote.nameWithOctave} out of range for {instrument_name}, by {steps_out_of_range} steps")
            
            noctaves = 1 + ( (abs(steps_out_of_range)-1) // 12)
            semitones = 12 * noctaves
            if steps_out_of_range <0:
                tintval = interval.Interval(semitones)
            elif steps_out_of_range > 0:
                tintval = interval.Interval(-semitones)
            else:
                tintval = interval.Interval(0)
            #
            # transpose does not return a value if inPlace == True
            #
            newnote = anote.transpose(tintval, inPlace=inPlace)
        else:
            newnote = anote
            
        return newnote
    
if __name__ == '__main__':
    print(Instruments.__doc__)
    instruments = Instruments()
    if instruments.verbose > 0:
        print(instruments.instruments_pd)
        print(instruments.clefs_pd)
    print(instruments.instruments_pd.loc['Flute'])
    
    
    