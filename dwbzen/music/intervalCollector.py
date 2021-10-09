
# ------------------------------------------------------------------------------
# Name:          intervalCollector.py
# Purpose:       Note collector class.
#
#                IntervalCollector creates a MarkovChains from a Note stream for the Intervals. 
#                The corresponding Producer class is PartProducer which reverses the process.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import music
import pandas as pd
from music21 import  interval, converter, corpus


class IntervalCollector(music.MusicCollector):

    def __init__(self, state_size=2, verbose=0, source=None, parts=None):
        super().__init__(state_size, verbose, source, parts)        # this also executes self.set_source()
        self.terminal_object = interval.Interval(99)
        self.initial_object = interval.Interval(0)
        self.markovChain.collector = IntervalCollector        self.countsFileName = '_intervalCounts'
        self.chainFileName = '_intervalsChain'
        
    def __repr__(self):
        # this should return a serialized form 
        return f"IntervalCollector {self.order}"
    
    def __str__(self):
        return f"IntervalCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}"

    def get_base_type(self):
        return interval.Interval
    
    def process(self, key_intervals, next_interval):
        index_str = music.Utils.show_intervals(key_intervals,'semitones')
        col_str = str(next_interval.semitones)
        col_name = next_interval.interval.directedName
        
        if self.verbose > 0:
            print(f"key_interval: {index_str}, next_interval: {next_interval.semitones}, {col_name}")
    
        if len(self.counts_df) == 0:
            # initialize the counts DataFrame
            self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[next_interval.semitones])
        else:
            if index_str not in self.counts_df.index:   # add a new row
                self.counts_df.loc[index_str, col_str] = 1
                # self.counts_df.loc[index_str, col_name] = 1
            else: # update existing index
                if col_str in self.counts_df.columns:
                    self.counts_df.loc[index_str, col_str] = 1 + self.counts_df.loc[index_str, col_str]
                else:
                    self.counts_df.loc[index_str, col_str] = 1
        self.counts_df = self.counts_df.fillna(0)

    def set_source(self, source):
        """This method is called in the __init__ of the parent class, MusicCollector
        
        Determine if source is a file or folder and if it exists (or not)
        Source can be a single file, or a composer name (such as 'bach')
        A single file must be compressed musicXML (.mxl), uncompressed (.musicxml), or .xml
        An xml file is treated as an uncompressed musicXML file
        A single file that resides in the music21 corpus is specified without an extension.
        The default corpus location ("/Compile/music21/music21/corpus") may be changed by setting corpus_folder attribute
        It may be accessed symbolically on the command line by the $CORPUS variable.
        Examples:
        --source composer='bach'                    # corpus search for composer 'bach'
        --source title='bwv*'                       # corpus wild card search
        --source "composer='bach',title='bwv*'"     # corpus wild card search for composer and title
        --source $CORPUS/haydn/opus74no1            # an individual corpus file
        --source '/data/music/Corpus/dwbzen/Prelude.mxl'    # a single musicXML file. The .mxl may be omitted
        --source [filename].json                    # load a serialized interval DataFrame (TODO)
        
        """
        result = True
        title = None
        composer = None
        if source.startswith('$CORPUS'):
            corpus_file = self.corpus_folder + source[6:]
            self.score = corpus.parse(corpus_file)
        elif 'composer' in source or 'title' in source:
            search_string = source.split(",")
            for ss in search_string:
                st = ss.split('=')
                if st[0] == 'composer':
                    composer = st[1]
                elif st[0] == 'title':
                    title = st[1]
            self.intervals_df = music.Utils.get_all_score_intervals(composer=composer, title=title) 
            if self.intervals_df is None or len(self.intervals_df) == 0:
                result = False
        else:   # must be a single filename or path
            file_info = music.Utils.get_file_info(source)
            if file_info['Path'].exists():
                self.score = converter.parse(file_info['path_text'])
                if self.verbose > 2:
                    print(self.score)
            if self.score is not None:
                self.intervals_df = music.Utils.get_intervals_for_score(self.score, self.part_names, self.part_numbers)
            else:
                result = False
        return result

    def collect(self):
        """
        Run collection using the set parameters
        Returns MarkovChain result
        """
        if self.verbose > 1:
            print(f"intervals: {self.intervals_df}")
        if self.intervals_df is not None:
            df_len = len(self.intervals_df) 
            iloc = 0
            while iloc + self.order < df_len:
                key_intervals = self.intervals_df.iloc[iloc:iloc+self.order]    # list of length self.order
                next_interval = self.intervals_df.iloc[iloc+self.order]
                self.process(key_intervals, next_interval)      # add to counts DataFrame
                
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
        self.chain_df = self.chain_df.applymap(lambda x: music.Utils.round_values(x, 6))
        self.markovChain.chain_df = self.chain_df
        
        if self.verbose > 0:
            print(f" Counts:\n {self.counts_df}")
            print(f" MarkovChain:\n {self.markovChain}")
            if self.verbose > 1:
                print(self.markovChain.__repr__())

        return self.markovChain
    
    def save(self):
        save_result = super().save()
        if self.intervals_df is not None:
            #
            # optionally save intervals_df as .csv
            #
            filename = "{}/{}_intervals.{}".format(self.save_folder, self.name, "csv")
            df = self.intervals_df[['name','niceName','semitones','part_name','part_number']]
            df.to_csv(filename)
        return save_result
        
    if __name__ == '__main__':
        print(IntervalCollector.__doc__)
        
