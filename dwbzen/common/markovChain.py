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
from common.characterCollector import CharacterCollector

class MarkovChain(object):

    def __init__(self, state_size=2, myname=''):
        self.order = state_size
        self.name = myname              # used when persisting to CSV or JSON
        self.chain = pd.DataFrame()
        pass
    
    def add_key(self, key, next_token, probability):
        prob_tupple = (probability, next_token)
        if key in self.chain:
            pass
        
    
    if __name__ == '__main__':
        print('Sample usage')
        collector = CharacterCollector(2)
        print(collector.__repr__())
        #
        # Example with strings
        #
        

