# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       Base Producer class.
#
#
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import pandas as pd

class Producer:
    
    def __init__(self, chain, min_size=0, max_size=0, trace = False):
        self.markov_chain = chain
        self.order = chain.order
        self.min_size = min_size
        self.max_size = max_size
        self.trace = trace
        
    def __repr__(self):
        return f"Producer {self.order}"


        
