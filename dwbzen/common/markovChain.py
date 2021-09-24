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

import json
import pandas as pd

class MarkovChain(object):

    def __init__(self, state_size=2, chain_df=pd.DataFrame(), myname=None):
        self.order = state_size
        self.name = myname          # used when persisting to CSV, Excel, or JSON
        self.chain_df = chain_df
        self.collector = None       # the Collector type
    
    def __repr__(self, *args, **kwargs):
        return self.chain_df.to_json(path_or_buf = None,orient='index')
    
    def __str__(self):
        return self.chain_df.to_csv(path_or_buf = None, line_terminator='\n')
    
    if __name__ == '__main__':
        print('MarkovChain')


