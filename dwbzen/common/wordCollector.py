# -*- coding: utf-8 -*- 
# ------------------------------------------------------------------------------
# Name:          wordCollector.py
# Purpose:       WordCollector class.
#
#                WordCollector creates a MarkovChain
#                from a word stream (strings). The corresponding
#                Producer class is SentenceProducer which reverses the process.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright � 2022 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from common.collector import Collector
from common.textParser import TextParser
import pandas as pd

import re

class WordCollector(Collector):
    """Create a Markov chain of words from a body of text.
    
    WordCollector analyzes word collections (Strings delimited by white space and/or punctuation) 
    and collects statistics in the form of a MarkovChain that can be used by a Producer class.
    
    For a given string (inline or from a file/stream), this examines all the word collections
    of a given length 1 to n (n <= 5), and records the #instances of each word that
    follows that word collection. Sentences are formed left to right advancing 1 Word each iteration.
    
    Features used in the corresponding SentenceProducer class:
    Sentence ending punctuation (. ! ?) is retained as a word to indicate the end of a sentence.
    A prefix (default is a space) is prepended to the first word of each sentence/line to indicate an initial word.
    
    There are three collection modes: words, sentences, and lines.
    The collection mode determines the set of initial keys. An initial key indicates the
    start of some unit - a sentence or line (which may have > 1 sentence).
    In 'words' collection mode, there are no initial keys - all the words treated equally.
    

    """
    
    def __init__(self, state_size=2, verbose=0, source=None, text=None, maxlines=None, ignore_case=True, remove_stop_words=False):
        super().__init__(state_size, verbose, source,  domain='text')
        self.text = text
        self.processing_mode = 'sentences'         # set by command line arguments to 'words' or 'sentences'
        
        self._text_parser = None
        self.ignore_case = ignore_case
        self._maxlines = maxlines
        self._remove_stop_words = remove_stop_words
        self._terminal_object = '~'
        self._initial_object = ' '
        self._source = source
        self._words = None                  # words in order of appearance
        
        self.countsFileName = '_wordCounts' + '_0{}'.format(state_size)
        self.chainFileName = '_wordsChain' + '_0{}'.format(state_size)
        
        self.words_re = re.compile(r'[,;: ]')    # regular expression to split a line into words

    def __str__(self):
        return f"WordCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}, text={self.text}, ignoreCase={self.ignoreCase}"


    def _process_words(self, words:list) -> pd.DataFrame:
        """Process a list of words to create a counts_df DataFrame
        
        The algorithm is identical to that used in CharacterCollector
        the difference being this operates on words instead of individual characters.
        counts_df DataFrame has 3 columns: 'key', 'word', and 'count' and a range index.
        key is a string of n-words where n is the order (state space size) of the MarkovChain model
        Initial keys are prefixed by TextParser._prefix, which defaults to a space.
        
        """
        word_keys =  [ (' '.join(words[i:i+self.order]), words[i+self.order]) for i in range(0, len(words)-2) ]
        word_keys_df =  pd.DataFrame(data=word_keys, columns=['key','word'])
        words_ser = word_keys_df.value_counts(ascending=False)
        df = pd.DataFrame(words_ser, columns=['count'])
        self.counts_df = df.reset_index()
        if self.sort_chain:
            self.counts_df.sort_values(by=['key','word'], ignore_index=True, inplace=True)
            
        return self.counts_df

    def _set_keys(self):
        prefix = self._text_parser.initial_word_prefix
        self._initial_keys_df = self.counts_df[ [x.startswith(prefix) for x in self.counts_df['key']] ]
        #
        # initiial_keys and keys are both sets and so the values are unique
        #
        self._initial_keys = set(self._initial_keys_df['key'].values.tolist())
        self._keys = set(self.counts_df['key'].values.tolist())
        if self.verbose > 0:
            print(f'total number of keys: {len(self._keys)}')
            print(f'number of initial keys: {len(self._initial_keys)}')
    
    def collect(self):
        self._text_parser = TextParser(txt=self.text, source=self._source, \
                   maxlines=self._maxlines, ignore_case=self.ignore_case, \
                   remove_stop_words=self._remove_stop_words)
        #
        # word counts are informational only
        #
        self.word_counts = self._text_parser.get_word_counts(sort_counts=True, reverse=True)
        self.words_df = self._text_parser.counts_df
                
        if self.processing_mode == 'words':
            self._collect_words()
        elif self.processing_mode == 'sentences':
            self._collect_sentences()
        elif self.processing_mode == 'lines':
            self._collect_lines()
        
        # create the MarkovChain from the counts by summing probabilities
        if self.counts_df.size > 0:
            self._set_keys()
            self._create_chain(initial=True)
            

    def _collect_lines(self) -> pd.DataFrame:
        """Run collection on a list of lines  using the set parameters
        
        Returns: MarkovChain result
        """
        #
        # get the words in the order they appear in the text
        #
        self._words = self._text_parser.get_line_words()
        return self._process_words(self._words)
        
            
    def _collect_sentences(self) -> pd.DataFrame:
        """Run collection on a list of sentences using the set parameters
        
        Returns: MarkovChain result
        """
        #
        # get the words in the order they appear in the text
        #
        self._words = self._text_parser.get_sentence_words()
        return self._process_words(self._words)
        

    def _collect_words(self) -> pd.DataFrame:
        """Run collection on a list of words
        
        Returns: MarkovChain result
        """

        #
        # get the words in the order they appear in the text
        #
        if self._remove_stop_words:
            self._words = self._text_parser.get_words()
        else:
            self._words = self._text_parser.get_all_words()
        
        #
        # create a counts_df DataFrame
        #
        return self._process_words(self._words)


    def save(self):
        save_result = super().save()
        return save_result

if __name__ == '__main__':
    print(WordCollector.__doc__())
        