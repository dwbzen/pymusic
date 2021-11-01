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
from music21 import note, clef
import music
import pandas as pd
import importlib

class Instruments(object):
    """Encapsulates instrument information for supported instrument:
       * Clef to use
       * range (low, high)
       * associated music21 class and class instance
    Instrument information maintained in resources/music/instruments.json
    Clef information in resources/music/clefs.json
    
    """
    
    instrument_names=[ 'Alto', 'Bass', 'Bassoon', 'Clarinet', 'Flute', 'Harpsichord', 'Koto', 'Oboe', 'Piano', 'PianoLH', 'PianoRH', 'Soprano', 'Tenor']
    clef_names=['Soprano', 'Alto', 'Tenor', 'Bass', 'Treble', 'Treble8va', 'Treble8vb', 'Bass8va', 'Bass8vb', 'C', 'F', 'G']
    
    def __init__(self, verbose=0):
        self.resource_folder="/Compile/dwbzen/resources/music"
        self.verbose = verbose
        self.__create_instrument_classes()
        self.__create_clef_classes()

    @staticmethod
    def __create_instance(row:pd.Series) -> Music21Object:
        module = row['module']
        class_name = row['class']
        my_module = importlib.import_module(module)
        MyClass = getattr(my_module, class_name)
        instance = MyClass()
        return instance
    
    def __create_instrument_classes(self):
        self.instruments_pd = pd.read_json(self.resource_folder + "/instruments.json", orient="index")
        self.instruments_pd['instance'] = [Instruments.__create_instance(row[1]) for row in self.instruments_pd.iterrows()]
    
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
    
    def check_range(self, instrument, note:note.Note) -> int:
        pass
        
    if __name__ == '__main__':
        print(music.Instruments.__doc__)
        instruments = music.Instruments()
        print(instruments.instruments_pd)
        print(instruments.clefs_pd)
    
    