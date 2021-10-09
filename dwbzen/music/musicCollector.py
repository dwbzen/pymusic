
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
from music21 import  interval, corpus, converter, duration, note

class MusicCollector(common.Collector):
    
    def __init__(self, state_size=2, verbose=0, source=None, parts=None):
        super().__init__(state_size, verbose, source)
        self.terminal_object = None     # set in derived classes
        self.initial_object = None      # set in derived classes
        self.score = None       # if source is a single Score
        self.part_names = []
        self.part_numbers = []
        self.parts = None
        self.save_folder="/Compile/dwbzen/resources/music"
        self.corpus_folder="/Compile/music21/music21/corpus"    # the default corpus folder
        if parts is not None:
            self.add_parts(parts)
        if source is not None:
            self.source = self.set_source(source)   # otherwise it's None
    
    def add_parts(self, parts):
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
    
    
    def save(self):
        save_result = super().save()
        return save_result
        