'''
Created on Oct 30, 2026

@author: don_bacon
'''

from music21 import interval, instrument
from music.instruments import Instruments

class GeneralUtils(object):
    """ General music utility functions
    """

    def __init__(self, params):
        pass
    
    @staticmethod
    def get_instrument(instrument_name:str)->(instrument.Instrument, interval.Interval):
        """ Consider creating another utils class (GeneralUtils) so there is no cross-dependency on MusicUtils or vise-versa
        """
        if instrument_name == "Piano":
            part_instrument = instrument.Piano()
            transpose_interval = interval.Interval(0)
        else:    # need to load Instruments and Clefs data
            instruments = Instruments()
            if instrument_name in instruments.instrument_names:
                part_instrument = instruments.get_instrument(instrument_name)
                interval_semitones = 0 if part_instrument.transposition is None else -part_instrument.transposition.semitones
                transpose_interval = interval.Interval(interval_semitones)
                part_instrument
            else:
                raise(TypeError(f"No dota for {instrument_name}"))
            
        return part_instrument,transpose_interval
    