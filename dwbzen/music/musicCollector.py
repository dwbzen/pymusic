
# ------------------------------------------------------------------------------
# Name:          noteCollector.py
# Purpose:       Base music collector class. Subclasses: NoteCollector, IntervalCollector
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import common
import music
import pandas as pd

class MusicCollector(common.Collector):
    
    def __init__(self, state_size=2, verbose=0, source=None, parts=None):
        super().__init__(state_size, verbose, source)
        self.terminal_object = None     # set in derived classes
        self.initial_object = None      # set in derived classes
        self.score = None       # if source is a single Score
        self.part_names = []    # optional part names used to filter parts of score(s)
        self.part_numbers = []  # optional part numbers used to filter parts
        self.parts = None       # comma-delimited part names from the command line
        self.score_partNumbers = []     # the part numbers extracted from the score or scores
        self.score_partNames = []       # the part names extracted from the score or scores
        self.durationCollector = None
        self.durations_df = None
        self.save_folder="/Compile/dwbzen/resources/music"
        self.corpus_folder="/Compile/music21/music21/corpus"    # the default corpus folder
        if parts is not None:
            self.add_parts(parts)
    
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
        