
# ------------------------------------------------------------------------------
# Name:          intervalCollector.py
# Purpose:       Interval collector class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2023 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from music.musicCollector import MusicCollector
from music.musicUtils import MusicUtils
from common.markovChain import MarkovChain
from common.collectorProducer import CollectorProducer
import pandas as pd
from music21 import  interval, converter, corpus

class IntervalCollector(MusicCollector):
    """IntervalCollector creates a MarkovChains from a the Intervals in Score Notes.
    
    """
    
    terminal_object = interval.Interval(100)
    initial_object = interval.Interval(99)

    def __init__(self, state_size=2, verbose=0, source=None, parts=None):
        super().__init__(state_size, verbose, source, parts)
        
        self.initial_object, self.terminal_object = IntervalCollector.initialize_initial_terminal_objects()
        self.countsFileName = '_intervalsCounts' + '_0{}'.format(state_size)
        self.chainFileName = '_intervalsChain' + '_0{}'.format(state_size)
        if source is not None:
            self.source = self.set_source(source)   # otherwise it's None
    
    @staticmethod
    def initialize_initial_terminal_objects() -> (pd.DataFrame, pd.DataFrame):
        initial_dict = {'interval':IntervalCollector.initial_object, 'name':IntervalCollector.initial_object.name, 'directedName':IntervalCollector.initial_object.directedName,\
                        'niceName':IntervalCollector.initial_object.niceName, 'semitones':IntervalCollector.initial_object.semitones, 'part_number':1, 'part_name':'initial'}
        terminal_dict = {'interval':IntervalCollector.terminal_object, 'name':IntervalCollector.terminal_object.name, 'directedName':IntervalCollector.terminal_object.directedName,\
                        'niceName':IntervalCollector.terminal_object.niceName, 'semitones':IntervalCollector.terminal_object.semitones, 'part_number':1, 'part_name':'terminal'}
        initial_object = pd.DataFrame(data=initial_dict, index=[0]) 
        terminal_object = pd.DataFrame(data=terminal_dict, index=[0])
        return initial_object, terminal_object
        
    def __repr__(self):
        # TODO: this should return a serialized form 
        return f"IntervalCollector {self.order}"
    
    def __str__(self):
        return f"IntervalCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}"

    def get_base_type(self):
        return interval.Interval
    
    def process(self, key_intervals, next_interval):
        index_str = MusicUtils.show_intervals(key_intervals,'semitones')
        col_str = str(next_interval.semitones)
        col_name = next_interval.interval.directedName
        
        if self.verbose > 1:
            print(f"key_interval: {index_str}, next_interval: {next_interval.semitones}, {col_name}")
    
        if self.counts_df is None:
            # initialize the counts DataFrame
            self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[next_interval.semitones])
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
        """Determine if source is a file or folder and if it exists (or not)
        
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
            MusicUtils.verbose = self.verbose
            self.intervals_df, self.score_partNames, self.score_partNumbers = \
                MusicUtils.get_all_score_music21_objects(interval.Interval, composer=composer, title=title, partnames=self.part_names, partnumbers=self.part_numbers) 
            if self.intervals_df is None or len(self.intervals_df) == 0:
                result = False
        else:   # must be a single filename or path
            file_info = MusicUtils.get_file_info(source)
            if file_info['Path'].exists():
                self.score = converter.parse(file_info['path_text'])
                if self.verbose > 2:
                    print(self.score)
            if self.score is not None:
                self.intervals_df, self.score_partNames, self.score_partNumbers = \
                    MusicUtils.get_music21_objects_for_score(interval.Interval, self.score, self.part_names, self.part_numbers)
            else:
                result = False
        return result

    def collect(self) -> MarkovChain:
        """
        Run collection using the set parameters
        Returns MarkovChain result
        """
        if self.verbose > 1:
            print(f"intervals: {self.intervals_df}")
            
        for pname in self.score_partNames:
            partIntervals_df = self.intervals_df[self.intervals_df['part_name']==pname]
            df_len = len(partIntervals_df)
            key_intervals = None
            next_interval = None
            iloc = 0

            while iloc + self.order < df_len:
                if iloc == 0:
                    key_intervals =  pd.concat([self.initial_object, partIntervals_df.iloc[iloc+self.order-1] ])
                else:
                    key_intervals = partIntervals_df.iloc[iloc:iloc+self.order]    # list of length self.order
                    
                next_interval = partIntervals_df.iloc[iloc+self.order]
                self.process(key_intervals, next_interval)      # add to counts DataFrame
                
                iloc = iloc + 1
            
            # add the terminal_object to signify and of the part
            key_intervals = partIntervals_df.iloc[iloc:]
            next_interval = self.terminal_object.iloc[0]
            self.process(key_intervals, next_interval)

        self.counts_df.rename_axis('KEY', inplace=True)
        if self.sort_chain:
            self.counts_df.sort_index('index', ascending=True, inplace=True)
            self.counts_df.sort_index(axis=1, ascending=True, inplace=True)
        #
        # create the MarkovChain from the counts by summing probabilities
        #
        sums = self.counts_df.sum(axis=1)
        self.chain_df = self.counts_df.div(sums, axis=0)
        self.chain_df.rename_axis('KEY', inplace=True)
        self.chain_df = self.chain_df.map(lambda x: MusicUtils.round_values(x, 6))
        
        self.markovChain = MarkovChain(self.order, self.counts_df,  chain_df=self.chain_df, myname=self.name)
        
        if self.verbose > 1:
            print(f" Counts:\n {self.counts_df}")
            print(f" MarkovChain:\n {self.markovChain}")
            if self.verbose > 1:
                print(self.markovChain.__repr__())
        #
        # collect durations from the Score and notes_df DataFrame
        #
        self.collect_durations(self.intervals_df)
        return self.markovChain
    
    def save(self):
        """Saves the chain_df, counts_df and intervals_df DataFrames to a file in specified format.
        
        """

        save_result = super().save()
        if self.intervals_df is not None:
            #
            # optionally save intervals_df as .csv
            #
            filename = "{}/{}_intervals.{}".format(self.save_folder, self.name, self.format)
            df = self.intervals_df[['name','niceName','semitones','part_name','part_number']]
            save_result = CollectorProducer.save_df(df, filename, self.format, orient='records')
        return save_result
        
if __name__ == '__main__':
    print(IntervalCollector.__doc__)
        
