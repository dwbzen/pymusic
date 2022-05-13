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

from datetime import datetime
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
    A space is prepended to the first word of each sentence to indicate a sentence starting word.
    
    TODO - add optional support for quotations by retaining the starting and ending double quotes on words.

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
        
        self.countsFileName = '_wordCounts'
        self.chainFileName = '_wordsChain'
        
        self.markovChain.collector = WordCollector
        self.words_re = re.compile(r'[,; ]')
        

    def __str__(self):
        return f"WordCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}, text={self.text}, ignoreCase={self.ignoreCase}"

    def process_sentences(self, sentences:[]) -> pd.DataFrame:

        now = datetime.now()
        sentence_number = 1
        size = len(sentences)
        for sentence in sentences:
            s = TextParser.remove_quotes(sentence)    # strip double quotes
            if self.ignore_case:
                s = s.lower()
            if self.verbose > 1:
                print(f'{sentence_number}  {sentence}\n    {s}\n')
            
            sentence_number += 1
            if  len(s) == 0:
                continue
            words = [w for w in re.split(self.words_re, s) if len(w)>0]
            if s[-1] in ".?!":
                words.append(s[-1])
            #
            # the first word of a sentence has a leading space
            #
            words[0] = f' {words[0]}'
            self.process_words(words)
            if sentence_number%100 == 0:
                print(f'{sentence_number} of {size}')
            
        delta = datetime.now() - now
        if self.verbose > 0:
            print(f'process_sentences execution time: {delta}')
          
        return self.counts_df
        
    def process_words(self, words:list) -> pd.DataFrame:
        """Process a list of words to create a counts DataFrame
        
        The algorithm is identical to that used in CharacterCollector
        the difference being this operates on words instead of individual characters.
        
        TODO speed this up 1218 sentences took process_sentences execution time: 0:24:14.364982
        
        """
        text_len = len(words)
        ind = 0         # index of current word
        more = text_len > self.order
        now = datetime.now()
        while more:
            index_str = ' '.join(words[ind:ind+self.order])
            col_str = words[ind+self.order]
            if self.verbose > 1:
                print(f"index_str: '{index_str}'  word: '{col_str}'")
            #
            # add the token index_str and the character that follows, col_str,
            # to the index and column list respectively
            # These will be the index= and columns= of the MarkovChain DataFrame
            #
            if len(self.counts_df) == 0:
                # initialize the counts DataFrame
                self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[col_str])
            else:
                if index_str not in self.counts_df.index:   # add a new row
                    self.counts_df.loc[index_str, col_str] = 1
                
                else:  # update existing index
                    if col_str in self.counts_df.columns:
                        self.counts_df.loc[index_str, col_str] = 1 + self.counts_df.loc[index_str, col_str]
                    else:
                        self.counts_df.loc[index_str, col_str] = 1
                        
            self.counts_df = self.counts_df.fillna(0)
            ind = ind + 1
            more = text_len > (ind + self.order)
        delta = datetime.now() - now
        
        if self.verbose > 1:
            print(f'process_words execution time: {delta}')
            
        return self.counts_df

    def collect(self):
        if self.processing_mode == 'words':
            self.collect_words()
        else:
            self.collect_sentences()

        
    def collect_sentences(self):
        """Run collection on a list of sentences using the set parameters
        
        Returns: MarkovChain result
        """
        now = datetime.now()
        self._text_parser = \
            TextParser(txt=self.text, source=self._source, maxlines=self._maxlines, ignore_case=self.ignore_case, \
                       remove_stop_words=self._remove_stop_words)
        delta = datetime.now() - now
        if self.verbose > 0:
            print(f'text_parser execution time: {delta}')
            
        self.process_sentences(self._text_parser.get_sentences())
        
        # create the MarkovChain from the counts by summing probabilities
        if self.counts_df.size > 0:
            super()._create_chain()
        
        return self.markovChain

    def collect_words(self):
        """Run collection on a list of words using the set parameters
        
        This is an alternative to processing on sentences (which is the default).
        Returns: MarkovChain result
        """
        self._text_parser = \
            TextParser(txt=self.text, source=self._source, maxlines=self._maxlines, ignore_case=self._ignoreCase, remove_stop_words=self._remove_stop_words)
        self.word_counts = self._text_parser.get_word_counts(sort_counts=True, reverse=True)
        self.words_df = self._text_parser.counts_df
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
        self.process_words(self._words)
        
        # create the MarkovChain from the counts by summing probabilities
        super()._create_chain()
        
        return self.markovChain
        

    def save(self):
        save_result = super().save()
        return save_result

        