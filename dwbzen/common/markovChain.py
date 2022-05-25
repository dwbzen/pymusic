# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:          markovChain.py
# Purpose:       
#
# Authors:       Donald Bacon
#
# Copyright:    Copyright © 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

'''
 MarkovChain is an implementation of a discreet-time Markov Chain (DTMC) with memory.
 It undergoes transitions from one state to another on a state space, 
 with the probability distribution of the next state depending only on the current state
 and not on the sequence of events that preceded it.
 The states are T instances, transitions from state T1 to state T2 are K instances
 each transition has an associated probability and additional information
 used by classes that generate Ts.</p>
  
 The order of the MarkovChain is the number of states that determine future states.
'''

import pandas as pd

class MarkovChain(object):

    def __init__(self, state_size, counts_df:pd.DataFrame, chain_df:pd.DataFrame=None, chain_dict:dict = None, myname:str=None):
        """Create and initialize a MarkovChain from a DataFrame or dict
        
        Either chain_df or chain_dict must be not None.
        Parameters:
            state_size - the MarkovChain order, also the logical size of the keys
            counts_df - a counts DataFrame
            chain_df - if not None, an existing chain DataFrame
            chain_dict - if not None, a dict of DataFrames used to create the chain DataFrame
        """
        self.order = state_size
        self.counts_df = counts_df
        self.name = myname          # used when persisting to CSV, Excel, or JSON
        self.chain_df = chain_df
        self.chain_dict = chain_dict
        if chain_dict is not None:
            self._create_chain_from_dict()
    
    def __repr__(self, *args, **kwargs):
        return self.chain_df.to_json(path_or_buf = None,orient='index')
    
    def __str__(self):
        return self.chain_df.to_csv(path_or_buf = None, line_terminator='\n')
    
    def _create_chain_from_dict(self):
            for key in self.chain_dict.keys():
                keycount_df = self.chain_dict[key]
                if self.chain_df is None:
                    self.chain_df = pd.DataFrame(keycount_df)
                else:
                    self.chain_df = pd.concat([self.chain_df, keycount_df], ignore_index= True)
    
    def get_rows(self, key) -> pd.DataFrame:
        """Returns the rows of the chain DataFrame for a given key
        If key not present, return DataFrame will have len==0 
        """
        return self.chain_df[self.chain_df['key'] ==key]
        
    if __name__ == '__main__':
        print('MarkovChain')


