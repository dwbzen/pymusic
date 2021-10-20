
# ------------------------------------------------------------------------------
# Name:          noteCollector.py
# Purpose:       Note collector class.
#
#                NoteCollector creates a pair of MarkovChains
#                from a Note stream (strings) for the Notes and Durations.
#                The corresponding Producer class is PartProducer which reverses the process.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import music
import common
import pandas as pd
from music21 import  converter, corpus, note

class NoteCollector(music.MusicCollector):

    def __init__(self, state_size=2, verbose=0, source=None, parts=None):
        super().__init__(state_size, verbose, source, parts)
        self.initial_object, self.terminal_object = self.initialize_initial_terminal_objects()
        self.markovChain.collector = NoteCollector
        self.countsFileName = '_noteCounts'
        self.chainFileName = '_notesChain'
        if source is not None:
            self.source = self.set_source(source)   # otherwise it's None
            
    def initialize_initial_terminal_objects(self) -> (pd.DataFrame, pd.DataFrame):
        initial_object = note.Rest()
        initial_object.duration.quarterLength=0
        terminal_object = note.Rest()
        terminal_object.duration.quarterLength=24
        initial_dict = {'note':initial_object, 'part_number':1, 'part_name':'rest', \
               'nameWithOctave':'rest', 'pitch':'', 'duration':initial_object.duration, \
                'pitchClass':0, 'name':'rest'}
        terminal_dict = {'note':terminal_object, 'part_number':1, 'part_name':'rest', \
               'nameWithOctave':'rest', 'pitch':'', 'duration':terminal_object.duration, \
                'pitchClass':0, 'name':'rest'}
        initial_object = pd.DataFrame(data=initial_dict, index=[0]) 
        terminal_object = pd.DataFrame(data=terminal_dict, index=[0])
        return initial_object, terminal_object
        
    def __repr__(self):
        return f"NoteCollector {self.order}"
    
    def __str__(self):
        return f"NoteCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}"

    def get_base_type(self):
        return note.Note
    
    def process(self, key_notes, next_note) -> (pd.DataFrame, pd.Series):
        """Adds key_notes and next_note to counts_df DataFrame
        
        """
        index_str = music.Utils.show_notes(key_notes,'nameWithOctave')
        col_str = str(next_note.nameWithOctave)
        if self.verbose > 1:
            print(f"key_note: {index_str}, next_note: {col_str}")
        
        if len(self.counts_df) == 0:
            # initialize the counts DataFrame
            self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[next_note.nameWithOctave])
        
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
        --source [filename].json                    # load a serialized notes DataFrame (TODO)
        
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
            self.notes_df, self.score_partNames, self.score_partNumbers = music.Utils.get_all_score_music21_objects(note.Note, composer=composer, title=title) 
            if self.notes_df is None or len(self.notes_df) == 0:
                result = False
        else:   # must be a single filename or path
            file_info = music.Utils.get_file_info(source)
            if file_info['Path'].exists():
                self.score = converter.parse(file_info['path_text'])
                if self.verbose > 2:
                    print(self.score)
            if self.score is not None:
                self.notes_df, self.score_partNames, self.score_partNumbers = music.Utils.get_music21_objects_for_score(note.Note, self.score, self.part_names, self.part_numbers)
            else:
                result = False
        return result
    
    def collect(self) -> common.MarkovChain:
        """Run collection on the notes_df DataFrame extracted from the source
        
        The collection unit is a score part name. Score part_names are in self.score_partNames set.
        The first MarkovChain key entry will consists of the initial_object + the first order-1 notes.
        The last entry will have the terminal_object as the last note.
        Returns MarkovChain result
        """
        if self.verbose > 1:
            print(f"notes: {self.notes_df}")
        for pname in self.score_partNames:
            partNotes_df = self.notes_df[self.notes_df['part_name']==pname]
            df_len = len(partNotes_df)
            next_note = None
            key_notes = None
            iloc = 0
            while iloc + self.order < df_len:
                if iloc == 0:
                    key_notes = self.initial_object.append( partNotes_df[iloc:iloc+self.order-1])
                else:
                    key_notes = partNotes_df.iloc[iloc:iloc+self.order]
                next_note = partNotes_df.iloc[iloc+self.order]
                self.process(key_notes, next_note)      # add to counts DataFrame
                
                iloc = iloc + self.order
            # add the terminal_object to signify and of the part
            key_notes = partNotes_df.iloc[iloc-1:iloc+self.order]
            next_note = self.terminal_object.iloc[0]
            self.process(key_notes, next_note)

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
        
        if self.verbose > 1:
            print(f" Counts:\n {self.counts_df}")
            print(f" MarkovChain:\n {self.markovChain}")
            if self.verbose > 1:
                print(self.markovChain.__repr__())
        #
        # collect durations from the Score and notes_df DataFrame
        #
        run_results = self.collect_durations(self.notes_df)
        return self.markovChain

    
    def save(self):
        save_result = super().save()
        if self.notes_df is not None and self.name is not None:
            #
            # optionally save notes_df as .csv
            #
            filename = "{}/{}_notes.{}".format(self.save_folder, self.name, "csv")
            df = self.notes_df[['name','nameWithOctave','pitchClass','part_name','part_number']]
            df.to_csv(filename)
        return save_result
    
    if __name__ == '__main__':
        print(NoteCollector.__doc__)
