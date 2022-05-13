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
        
        self.markovChain.collector = CharacterCollector

    def __str__(self):
        return f"CharacterCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}, text={self.text}, ignoreCase={self._ignore_case}"
    
    def process(self, line):
        line = line.replace('\n', self.terminal_object)
        #
        #
        if self.ignore_case:
            line = line.lower()
        line_len = len(line)
        ind = 0         # index of current character
        more = line_len > self.order    # more to go?
        while more:
            index_str = line[ind:ind+self.order]
            col_str = line[ind+self.order]
            if self.verbose >= 2:
                print(f"token {index_str}  char '{col_str}'")
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
            more = line_len > (ind + self.order)
        
    
    def collect(self):
        """
        Run collection using the set parameters
        Returns MarkovChain result
        """
        if self.source is not None:
            with open(self.source, "r") as f:
                lnum = 1
                for line in f:
                    if self.verbose > 1:
                        print(f"line {lnum}\t{line}", end='')
                    line = self.initial_object + line.strip() + self.terminal_object     # add intial and terminal characters (typically a space)
                    self.process(line)
                    lnum = lnum + 1
        elif self.text is not None:
            # add initial and terminal characters if needed
            txt = self.initial_object + self.text.strip() + self.terminal_object
            self.process(txt)
        #
        # create the MarkovChain from the counts
        #
        super()._create_chain()
        
        return self.markovChain
        
    def save(self):
        save_result = super().save()
        return save_result
    
if __name__ == '__main__':
    print(CharacterCollector.__doc__())
