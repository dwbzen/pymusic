
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
# Copyright:    Copyright (c) 2022 Donald Bacon
#
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from music.musicCollector import MusicCollector
from music.musicUtils import MusicUtils
from common.markovChain import MarkovChain
from common.collectorProducer import CollectorProducer
import pandas as pd
from music21 import  converter, corpus, note

class NoteCollector(MusicCollector):
    """Collect Notes from one or more scores into a MarkovChain
    
    There are 6 collection modes: absolute, diatonic, absolute pitch class, diatonic pitch class,
    scale degree number (sdn), and scale degree roman (sdr).
    In absolute mode the note pitches used are exactly those that appear in the score(s) without alteration.
    In diatonic mode, the pitch used is the diatonic equivalent for the Key of C-major.
    For example consider the note "F#5". Relative to the key of D-major this is the 3rd step in the scale.
    Transposing to C-major this becomes "E5".
    The same note relative to the score key of Bb-major is #5, so G# in C-Major.
    
    When transposing minor keys, the natural minor scale is used (which is the same as melodic minor descending)
    
    Absolute pitch class collects only the pitch class of each note. 
    Pitch class is a music21 pitch attribute that is an integer number from 0 to 11 where 0=C, 1=C# etc.
    Diatonic pitch class collects the pitch class of each note transposed to C-Major.
    The octave portion of the note is lost when collecting pitch class. 
    However the MusicProducer provides ways to reinsert an octave (for each part) when generating scores.
    
    Scale degree collects the scale degree of each pitch relative to the Key of the Part.
    Scale degree records the appropriate scale degree as an integer, 1 to 7.
    Both are relative to the underlying Key or Scale. And both prepend an accidental if there is one.
    
    Note that the Mode of the Scale makes a difference when collecting scale degrees.
    For example, E-minor and G-major have the same key signature, but the scale degrees are different -
    an 'e' is 1 in E-minor, but 6 in G-major. This can be problematic in some of the musicxml scores
    that have parts in minor mode.
    For example the music21 Bach corpus scores consistently have the "real" key in the Soprano part,
    the other parts the relative major.
    To account for this the collector includes two additional features: filter and keypart.
    If set, the filter will return only scores that meet the filter criteria. 
    At present the only filter supported is 'mode' which can have a values 'major' or 'minor'.
    Keypart is the part name that determines the actual (real) key. 
    If set, then the key to all parts is set to the keypart key.
    So the appropriate command-line arguements would be: --mode sd --filter "mode=minor" --keypart Soprano
    
    """
    
    initial_object = note.Note('C0')
    terminal_object = note.Note('C#8')
        
    def __init__(self, state_size=2, verbose=0, source=None, parts=None, collection_mode='dpc', enforce_range=True):
        super().__init__(state_size, verbose, source, parts)
        
        self.initial_object, self.terminal_object = NoteCollector.initialize_initial_terminal_objects()
        
        self.countsFileName = '_notesCounts_' + collection_mode + '_0{}'.format(state_size)
        self.chainFileName = '_notesChain_' + collection_mode + '_0{}'.format(state_size)
        self.notes_df_fileName = '_notes_df'        # self.notes_df saved
        
        self.notes_df = pd.DataFrame()
        self.collection_mode = collection_mode      # default is absolute pitch
        self.enforce_range = enforce_range          # applies only to dp and dpc collection modes

        self.number_of_scores = 0                   # can be >1 if searching a corpus
        self.transposed_scores = []                 # if collection mode is diatonic pitch or pitch class
        self.transposed_score = None                # a single score if diatonic collection
        MusicUtils.verbose = verbose
        
        self.pitch_class_mode = (collection_mode == 'dpc' or collection_mode == 'apc')
        self.pitch_mode =  (collection_mode == 'dp' or collection_mode == 'ap')
        self.scale_degree_mode = collection_mode.startswith('sd')
        self.diatonic = collection_mode.startswith('d')
        self.absolute = (collection_mode.startswith('a') or collection_mode.startswith('s'))

        #
        # collection_scores will reference self.scores if collection mode is absolute pitch or pitch class
        # or self.transposed_scores if collection mode is diatonic
        #
        self.collection_scores = []
        self.source_path = source
            
    @staticmethod
    def initialize_initial_terminal_objects() -> (pd.DataFrame, pd.DataFrame):

        initial_dict = {'note':NoteCollector.initial_object, 'part_number':1, 'part_name':'note', \
               'nameWithOctave':NoteCollector.initial_object.nameWithOctave, 'pitch':str(NoteCollector.initial_object.pitch), \
               'duration':NoteCollector.initial_object.duration, \
               'scaleDegree':'1', 'ps':12.0, \
               'pitchClass':NoteCollector.initial_object.pitch.pitchClass, 'name':NoteCollector.initial_object.name}
        
        terminal_dict = {'note':NoteCollector.terminal_object, 'part_number':1, 'part_name':'note', \
               'nameWithOctave':NoteCollector.terminal_object.nameWithOctave, 'pitch':str(NoteCollector.terminal_object.pitch), \
               'duration':NoteCollector.terminal_object.duration, \
               'scaleDegree':'#1', 'ps':109.0, \
               'pitchClass':NoteCollector.terminal_object.pitch.pitchClass, 'name':NoteCollector.terminal_object.name}
        
        initial_object = pd.DataFrame(data=initial_dict, index=[0]) 
        terminal_object = pd.DataFrame(data=terminal_dict, index=[0])
        return initial_object, terminal_object
        
    def __repr__(self):
        return f"NoteCollector {self.order}"
    
    def __str__(self):
        return f"NoteCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}"

    def get_base_type(self):
        return note.Note
    
    def set_source(self, source):
        """This method is called first in collect()
        
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
        range_instruments = None
        if self.enforce_range:
            range_instruments = self.instruments
               
        if 'composer' in source or 'title' in source:
            #
            # search the corpus for multiple scores
            # for example: "composer=bach,title=^bwv4+"
            #
            search_string = source.split(",", maxsplit=1)    # title can be a regular expression with embedded commas
            for ss in search_string:
                st = ss.split('=')
                if st[0] == 'composer':
                    composer = st[1]
                elif st[0] == 'title':
                    title = st[1]

            self.scores, self.titles = MusicUtils.get_scores_from_corpus(composer=composer, title=title, keypart=self.key_partName, filters=self.score_filters)
            self.number_of_scores = len(self.scores)
                
            for ascore in self.scores:
                if self.verbose > 0:
                    print(f"working on {ascore.metadata.title}")
                if self.diatonic:
                    #
                    # transpose the score if collection mode is diatonic
                    # default target key of C-Major  or A-minor is used
                    # based on the mode (major or minor) of the original Keys of each part
                    #                    
                    transposed_score = MusicUtils.transpose_score(ascore, partnames=self.part_names, instruments=range_instruments)
                    self.transposed_scores.append(transposed_score)
                    notesdf, pnames, pnums = MusicUtils.get_notes_for_score(transposed_score, self.part_names, self.part_numbers)
                else:
                    #
                    # absolute pitch/pitch class or scale degree.  no transposition, but still need to adjust_accidentals
                    #
                    transposed_score = MusicUtils.adjust_score_accidentals(ascore, partnames=self.part_names, inPlace=False)
                    self.transposed_scores.append(transposed_score)
                    notesdf, pnames, pnums = MusicUtils.get_notes_for_score(transposed_score, self.part_names, self.part_numbers)
                
                if self.verbose > 2 and len(notesdf)>0 and 3 in notesdf['pitchClass']:  # temporary debugging code
                    print(notesdf[notesdf['pitchClass']==3][['part_name','pitch']])
                    
                self.notes_df = pd.concat([self.notes_df, notesdf])  # deprecated:   self.notes_df.append(notesdf)
                if len(pnames) > 0:
                    self.score_partNames = self.score_partNames.union(pnames)
                if len(pnums) > 0:
                    self.score_partNumbers = self.score_partNumbers.union(pnums)
                
            if self.notes_df is None or len(self.notes_df) == 0:
                result = False
        else:
            #
            # a single filename or path - one score
            #
            if source.startswith('$CORPUS'):
                corpus_file = self.corpus_folder + source[6:]
                self.score = corpus.parse(corpus_file)
            else:
                file_info = MusicUtils.get_file_info(source)
                if file_info['Path'].exists():
                    self.score = converter.parse(file_info['path_text'])
                    if self.verbose > 2:
                        self.score.show()
            if self.score is not None:
                self.scores.append(self.score)
                self.number_of_scores = 1
                if self.diatonic:
                    # diatonic pitch - transpose the score to C-Major or C-Minor
                    # and enforce instrument ranges if needed (if enforce_range is True)
                    #
                    self.transposed_score = MusicUtils.transpose_score(self.score, partnames=self.part_names, instruments=range_instruments)
                    self.transposed_scores.append(self.transposed_score)
                    self.notes_df, self.score_partNames, self.score_partNumbers = \
                        MusicUtils.get_notes_for_score(self.transposed_score, self.part_names, self.part_numbers)
                else:   # absolute pitch/pitch class or scale degree - no transposition required
                    self.notes_df, self.score_partNames, self.score_partNumbers = \
                        MusicUtils.get_notes_for_score(self.score, self.part_names, self.part_numbers)
            else:
                result = False

        return result

    def process(self, key_notes:pd.DataFrame, next_note:pd.Series) -> (pd.DataFrame, pd.Series):
        """Adds key_notes and next_note to counts_df DataFrame
            In pitch mode the Note attribute counted is 'nameWithOctave' as in "C4"
            In pitch class mode the attribute is 'name' - so no octave, just the pitch, as in "C"
        
            Args:
                key_notes - a n-row DataFrame from notes_df where n = order of the MarkovChain
                next_note - a single row Series from notes_df that represents the Note following the key_notes
        """
        
        if self.pitch_mode:
            index_str = MusicUtils.show_notes(key_notes,'nameWithOctave')
            col_str = str(next_note.loc['nameWithOctave'])
        elif self.pitch_class_mode:
            index_str = MusicUtils.show_notes(key_notes,'name')
            col_str = str(next_note.loc['name'])
        else:  # self.scale_degree_mode:
            index_str = MusicUtils.show_notes(key_notes,'scaleDegree')
            col_str = str(next_note.loc['scaleDegree'])

        if self.verbose > 1:
            print(f"key_note: {index_str}, next_note: {col_str}")
        
        if self.counts_df is None:
            # initialize the counts DataFrame
            if self.pitch_mode:
                self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[next_note.nameWithOctave])
            elif self.pitch_class_mode:
                self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[next_note.loc['name']])
            else:  # self.scale_degree_mode:
                self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[next_note.loc['scaleDegree']])
        
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
            
    def collect(self) -> MarkovChain:
        """Run collection on the notes_df DataFrame created from the source score(s)
        
        The collection unit is a score part name. Score part_names are in self.score_partNames set.
        The first MarkovChain key entry will consists of the initial_object + the first order-1 notes.
        The last entry will have the terminal_object as the last note.
        Returns MarkovChain result
        """
        if self.source_path is not None:
            self.source = self.set_source(self.source_path)
            
        filename = "{}/{}{}.csv".format(self.save_folder, self.name, self.notes_df_fileName)
        self.notes_df.to_csv(path_or_buf=filename)
        print(f"notes: {filename}")
        
        for pname in self.score_partNames:

            partNotes_df = self.notes_df[self.notes_df['part_name']==pname]
            df_len = len(partNotes_df)
            next_note = None
            key_notes = None
            iloc = 0
            while iloc + self.order < df_len:
                if iloc == 0:
                    key_notes = pd.concat([self.initial_object, partNotes_df[iloc:iloc+self.order-1]] )   # deprecated: self.initial_object.append( partNotes_df[iloc:iloc+self.order-1])
                else:
                    key_notes = partNotes_df.iloc[iloc:iloc+self.order]
                
                next_note = partNotes_df.iloc[iloc+self.order]
                self.process(key_notes, next_note)      # add to counts DataFrame
                
                iloc = iloc + 1
                
            # add the terminal_object to signify end of this part
            key_notes = partNotes_df.iloc[iloc:]
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
        self.chain_df = self.chain_df.applymap(lambda x: MusicUtils.round_values(x, 6))
        
        self.markovChain = MarkovChain(self.order, self.counts_df,  chain_df=self.chain_df, myname=self.name)
        
        if self.verbose > 1:
            print(f" Counts:\n {self.counts_df}")
            print(f" MarkovChain:\n {self.markovChain}")
            if self.verbose > 1:
                print(self.markovChain.__repr__())
        #
        # collect durations from the Score and notes_df DataFrame
        #
        self.collect_durations(self.notes_df)
        return self.markovChain

    
    def save(self):
        """Saves the chain_df, counts_df, and notes_df DataFrames to a file in specified format.
        
        """
        save_result = super().save()
        if self.notes_df is not None and self.name is not None:
            #
            # optionally save notes_df as .csv
            #
            filename = "{}/{}_notes.{}".format(self.save_folder, self.name, self.format)
            df = self.notes_df[['name','nameWithOctave','pitchClass','ps','part_name','part_number','quarterLength', 'scaleDegree']]
            save_result = CollectorProducer.save_df(df, filename, self.format)
            #df.to_csv(filename)
        return save_result
    
if __name__ == '__main__':
    print(NoteCollector.__doc__)
