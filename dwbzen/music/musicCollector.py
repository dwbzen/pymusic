
# ------------------------------------------------------------------------------
# Name:          noteCollector.py
# Purpose:       Base music collector class. Subclasses: NoteCollector, IntervalCollector
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
#
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from common.collector import Collector
from .instruments import Instruments
import music
import pandas as pd

class MusicCollector(Collector):
    
    def __init__(self, state_size=2, verbose=0, source=None, parts=None):
        super().__init__(state_size, verbose, source, domain='music')
        
        self.instruments = Instruments(self.verbose)

        self.corpus_folder="/Compile/music21/music21/corpus"    # the default corpus folder
        self.terminal_object = None     # set in derived classes
        self.initial_object = None      # set in derived classes
        self.score = None       # if source is a single Score
        self.scores = []        # a list of Score if collecting from a corpus
        self.titles = []        # the titles of all Score(s)
        self.part_names = []    # optional part names used to filter parts of score(s)
        self.part_numbers = []  # optional part numbers used to filter parts
        self.parts = None       # comma-delimited part names from the command line
        self.score_partNumbers = set()     # the part numbers extracted from the score or scores
        self.score_partNames = set()       # the part names extracted from the score or scores
        self.durationCollector = None
        self.durations_df = None
        if parts is not None:
            self.add_parts(parts)
        self.enforceRange = True
        self.counts_df = None
        self.chain_df = None
        #
        # filter string to apply against Part(s)
        # format is: property=value, for example "mode=minor"
        # The filter is applied after the score_key is set (if it's not None)
        #
        self._filter = None
        self.score_filters = {}     # mode filter can be 'major' or 'minor'
        #
        # if key_partName is not None, all the Key for score parts is
        # set to the Key of the named part.
        # Essentially this becomes the Key to use for an entire Score
        #
        self.key_partName = None
    
        
    def set_score_filter(self, filter_string):
        if filter_string is not None and len(filter_string) >= 3 and '=' in filter_string:
            self._filter = filter_string
            temp = filter_string.split('=')
            if temp[0] == 'mode':
                self.score_filters['mode'] = temp[1]
            
    def add_parts(self, parts) -> str:
        if parts is not None:
            self.parts = parts
            parts_list = parts.split(",")   # could be numbers or names
            for p in parts_list:
                if p.isdigit():   # all digits
                    self.part_numbers.append(int(p))
                else:
                    self.part_names.append(p)               


    def collect(self):  # implement in derived classes
        return None
    
    def collect_durations(self, source:pd.DataFrame ):
        self.durationCollector = music.DurationCollector(self.order, self.verbose, source, self.parts)
        self.durationCollector.score = self.score
        if self.name is not None and len(self.name) > 0:
            self.durationCollector.name = self.name
        self.durationCollector.format = self.format
        self.durationCollector.sort_chain = self.sort_chain
        run_results = self.durationCollector.run()
        self.durations_df = self.durationCollector.durations_df
        return run_results
    
    def save(self):
        save_result = super().save()
        return save_result
        