# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:          intervalCollector.py
# Purpose:       Note collector class.
#
#                IntervalCollector creates a pair of MarkovChains
#                from a Note stream for the Intervals and Durations. 
#                The corresponding Producer class is PartProducer which reverses the process.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import music
import pandas as pd
import sys
from music21 import duration


class DurationCollector(music.MusicCollector):

    def __init__(self, state_size=2, verbose=0, source=None, parts=None):          # this also executes self.set_source()
        super().__init__(state_size, verbose, source)
        self.terminal_object = duration.Duration(24.0)      # equivalent to 6 x 4 quarter notes
        self.initial_object = duration.Duration(0.0)        # 0 duration have ordinal None
        self.score = None       # if source is a single Score
        self.part_names = []
        self.part_numbers = []
        self.parts = None
        self.durations_df = None
        self.source_df = None
        self.countsFileName = '_durationCounts'
        self.chainFileName = '_durationsChain'
        if parts is not None:
            self.add_parts(parts)
        if source is not None:
            self.source = self.set_source(source)   # otherwise it's None

    def __repr__(self):
        return f"DurationCollector {self.order}"
    
    def __str__(self):
        return f"DurationCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}"

    def get_base_type(self):
        return duration.Duration
    
    def process(self, key_durations, next_duration):
        index_str = music.Utils.show_durations(key_durations)
        col_str = str(next_duration.quarterLength)
        if self.verbose > 1:
            print(f"key_note: {index_str}, next_note: {col_str}")
        
        if len(self.counts_df) == 0:
            # initialize the counts DataFrame
            self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[str(next_duration.quarterLength)] )
        
        else:
            if index_str not in self.counts_df.index:   # add a new row
                self.counts_df.loc[index_str, col_str] = 1
            else: # update existing index
                if col_str in self.counts_df.columns:
                    self.counts_df.loc[index_str, col_str] = 1 + self.counts_df.loc[index_str, col_str]
                else:
                    self.counts_df.loc[index_str, col_str] = 1

        self.counts_df = self.counts_df.fillna(0)
        
    def set_source(self, source):
        """This method is called in the __init__ of the parent class, MusicCollector
        
        The source is notes DataFrame (notes_df) created by NoteCollector,
        or DataFrame (intervals_df) created by IntervalCollector
        """
        result = False
        if not isinstance(source, pd.DataFrame):
            # TODO: add support for stand-alone operation. 
            # TODO: Need to add DurationCollectorRunner and expand set_source() as in other MusicCollectors
            print("Invalid source", file=sys.stderr)
            return result
        self.source = source
        self.source_df = source
        self.durations_df = None
        result = True
        if self.source_df is not None:   # create the durations DataFrame
            self.durations_df = music.Utils.get_durations_from_notes(self.source_df)
        
        return result

        
    def collect(self):
        """
        Run collection using the set parameters
        Returns MarkovChain result
        """
        if self.verbose > 1:
            print(f"durations: {self.durations_df}")
            
        if self.durations_df is not None:
            df_len = len(self.durations_df) 
            iloc = 0
            while iloc + self.order < df_len:
                key_durations = self.durations_df.iloc[iloc:iloc+self.order]    # list of length self.order
                next_duration = self.durations_df.iloc[iloc+self.order]
                self.process(key_durations, next_duration)      # add to counts DataFrame
                
                iloc = iloc + self.order

        self.counts_df.rename_axis('KEY', inplace=True)
        if self.sort_chain:
            self.counts_df.sort_index('index', ascending=True, inplace=True)
            self.counts_df.sort_index(axis=1, ascending=True, inplace=True)

        #
        # create the MarkovChain from the counts by added probabilities
        #
        sums = self.counts_df.sum(axis=1)
        self.chain_df = self.counts_df.div(sums, axis=0)
        self.chain_df.rename_axis('KEY', inplace=True)
        self.chain_df = self.chain_df.applymap(lambda x: music.Utils.round_values(x, 3))
        self.markovChain.chain_df = self.chain_df
        
        if self.verbose > 1:
            print(f" Counts:\n {self.counts_df}")
            print(f" MarkovChain:\n {self.markovChain}")
            if self.verbose > 1:
                print(self.markovChain.__repr__())

        return self.markovChain

    
    def save(self):
        save_result = super().save()
        if self.durations_df is not None and self.name is not None:
            #
            # optionally save durations_df as .csv
            #
            filename = "{}/{}_durations.{}".format(self.save_folder, self.name, "csv")
            df = self.durations_df[['type','ordinal','dots','fullName','quarterLength','tuplets']]
            df.to_csv(filename)
        return save_result
    
    if __name__ == '__main__':
        print(DurationCollector.__doc__)
    