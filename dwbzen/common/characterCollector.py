# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:          characterCollector.py
# Purpose:       Character collector class.
#
#                CharacterCollector creates a MarkovChain
#                from a word stream (strings). The corresponding
#                Producer class is WordProducer which reverses the process.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright � 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from .collector import Collector
from common.textParser import TextParser
import pandas as pd

class CharacterCollector(Collector):

    def __init__(self, state_size=2, verbose=0, source=None, text=None, ignore_case=False):
        super().__init__(state_size, verbose, source,  domain='text')
        self.text = text
        self.ignore_case = ignore_case
        self.terminal_object = '~'
        self.initial_object = ' '

        self.countsFileName = '_charCounts'
        self.chainFileName = '_charsChain'
        
        self._text_parser = None

    def __str__(self):
        return f"CharacterCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}, text={self.text}, ignoreCase={self._ignore_case}"
    
    def process(self, keys, word):
        keys += [ (''.join(word[i:i+self.order]), word[i+self.order])  for i in range(0, len(word)-self.order)]
        
    def _set_keys(self):
        #
        # create the keys 
        #
        prefix = self.initial_object
        self._initial_keys_df = self.counts_df[ [x.startswith(prefix) for x in self.counts_df['key']] ]
        self._initial_keys = set(self._initial_keys_df['key'].values.tolist())
        self._keys = set(self.counts_df['key'].values.tolist())
        if self.verbose > 0:
            print(f'total number of keys: {len(self._keys)}')
            print(f'number of initial keys: {len(self._initial_keys)}')

    def collect(self):
        """
        Run collection using the set parameters
        Returns MarkovChain result
        """
        word_keys = []
        if self.source is not None:
            self._text_parser = TextParser(source=self.source, ignore_case=self.ignore_case, maxlines=None, remove_stop_words=False)
            #
            # word counts are informational only
            #
            self.word_counts = self._text_parser.get_word_counts(sort_counts=True, reverse=True)
            self.words_df = self._text_parser.counts_df
            for w in self._text_parser.get_line_words():
                word = self.initial_object + w.strip() + self.terminal_object
                if len(word) >= self.order:
                    self.process(word_keys, word)
    
        elif self.text is not None:
            # add initial and terminal characters if needed
            s_rempunc = TextParser.remove_punctuation(self.text)
            words = s_rempunc.split(' ')
            for w in words:
                word = self.initial_object + w.strip() + self.terminal_object
                if len(word) >= self.order:
                    self.process(word_keys, word)
        
        #
        # create the counts_df DataFrame
        #          
        word_keys_df =  pd.DataFrame(data=word_keys, columns=['key','word'])
        words_ser = word_keys_df.value_counts(ascending=False)
        df = pd.DataFrame(words_ser, columns=['count'])
        self.counts_df = df.reset_index()
        if self.sort_chain:
            self.counts_df.sort_values(by=['key','word'], ignore_index=True, inplace=True)
        
        # create the MarkovChain from the counts by summing probabilities
        if self.counts_df.size > 0:
            self._set_keys()
            self._create_chain(initial=False)
        
        return self.markovChain
        
    def save(self):
        save_result = super().save()
        return save_result
    
if __name__ == '__main__':
    print(CharacterCollector.__doc__())
