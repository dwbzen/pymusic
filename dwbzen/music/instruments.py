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
from common.environment import Environment
import pandas as pd
import importlib
import json
import argparse
from typing import List

class Instruments(object):
    """Encapsulates instrument and clefs information for the supported instruments. Attributes are:
       * module - the music21 module: music21.instrument
       * class - associated music21 class name. The class instance is created when Instruments is instantiated.
       * range - range of the instrument (low,high) in scientific pitch notation (note+octave), for example C2,Ab4
       * pitchRange - (low,high) integers as pitch pitch space attribute. Where 0 is C-1, 1 is C0 etc. 
           So pitchRange of a Bassoon of (C2,Ab4) is 34,76. It's a Music21 thing.
       * Clef to use. Enumerated in "clef_names"
       * transpose - True (1) if the instrument transposes, 0 otherwise
       * transpose_key - the "sounds" key, for example a transpose_key of Bb sounds a maj 2nd lower than written.
       * transpose_diatonic - given as a music21 DiatonicInterval: specifier ("M", "m", "P" for major, minor, perfect), 
               and the generic interval. For example, ("M', 3) for a major 3rd.
       * transpose_chromatic - #half steps
       * transpose_text - description of the transposition
    Instruments, Clefs maintained in resources/music/instruments.json, and resources/music/instruments.json respectively.
    """
    
    INSTRUMENTS_FILE = "instruments.json"
    CLEFS_FILE = "clefs.json"
    
    def __init__(self, verbose=0):
        env = Environment.get_environment()
        self.resource_folder = env.get_resource_folder("music")
        self.verbose = verbose
        instruments_filename = f"{self.resource_folder}/{Instruments.INSTRUMENTS_FILE}"
        clefs_filename =  f"{self.resource_folder}/{Instruments.CLEFS_FILE}"
        with open(instruments_filename, "r") as fp:
            instruments_dict = json.load(fp)
        with open(clefs_filename, "r") as fp:
            clefs_dict = json.load(fp)
        
        self._instruments = instruments_dict["instruments"]
        self._instrument_names = instruments_dict["instrument_names"]
        self._clef_names = clefs_dict["clef_names"]
        self._clefs = clefs_dict["clefs"]
        self._tags = instruments_dict["tags"]
        
        self.instruments_pd = self.__create_instrument_classes(self._instruments)
        self.clefs_pd = self.__create_clef_classes(self._clefs)
    
    @property
    def instruments(self)->dict:
        return self._instruments
    
    @property
    def clefs(self)->dict:
        return self._clefs
    
    @property
    def instrument_names(self)->List[str]:
        return self._instrument_names
    
    @property
    def clef_names(self)->List[str]:
        return self._clef_names

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
    
    def __create_instrument_classes(self, instruments:dict)->pd.DataFrame:
        column_names = self._tags
        index_names = self._instrument_names
        instruments_pd = pd.DataFrame(instruments, columns=column_names, index=index_names)
        instruments_pd['instance'] = [Instruments.__create_instance(row[1]) for row in instruments_pd.iterrows()]
        instruments_pd['range_ps'] = [Instruments.__define_pitch_range(row[1]) for row in instruments_pd.iterrows()]
        instruments_pd.fillna(value={'transpose':False}, inplace=True)
        instruments_pd.fillna(value={'transpose_diatonic':0}, inplace=True)
        instruments_pd.fillna(value={'transpose_chromatic':0}, inplace=True)
        instruments_pd.fillna(value={'transpose_text':'Non-transposing'}, inplace=True)
        instruments_pd.fillna(value={'transpose_key':'C-major'}, inplace=True)
        return instruments_pd
    
    def __create_clef_classes(self, clefs:dict)->pd.DataFrame:
        clefs_pd = pd.DataFrame(clefs, columns=["name", "module", "class"], index=self._clef_names)
        clefs_pd['instance'] = [Instruments.__create_instance(row[1]) for row in clefs_pd.iterrows()]
        return clefs_pd

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="increase output verbosity", action="count", default=0)
    parser.add_argument("--name", "-I", help="instrument name", type=str, default=None)
    parser.add_argument("--clef", "-C", help="clef name", type=str, default=None)
    parser.add_argument("--info", help="display class help", action="store_true", default=False)
    args = parser.parse_args()
    if args.info:
        print(Instruments.__doc__)
    instruments = Instruments(args.verbose)
    instrument_name = args.name.title()
    clef_name = args.clef.title() if args.clef is not None else None
    if instruments.verbose > 1:
        print(f"instruments DataFrame: {instruments.instruments_pd}")
        print(f"clefs DataFrame: {instruments.clefs_pd}")
    if args.name is not None:
        print(f"{args.name}:\n{instruments.instruments_pd.loc[instrument_name]}")
        m21Instrument = instruments.get_instrument(instrument_name)
        print(f"instrument: {type(m21Instrument)} : {m21Instrument}")
    
    if clef_name is not None:
        print(f"\n{args.clef} clef:\n{instruments.clefs_pd.loc[clef_name]}")
    
    