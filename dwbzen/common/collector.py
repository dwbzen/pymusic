# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:          collector.py
# Purpose:       Base collector class.
#                Collects data from a defined source and builds a MarkovChain
#                of a given order.
#                Collector subclasses are tailored to the specific data type
#                being collected and how that data is sourced.
#                A collector has a corresponding Producer class that takes
#                a MarkovChain as input and produces data.
#                For example, a CharacterCollector creates a MarkovChain
#                from a word stream (strings). The WordProducer reverses the process.
#
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright � 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import pandas as pd
import common

class Collector:
    
    def __init__(self, state_size=2, verbose=0, source=None):
        self.order = state_size
        self.verbose = verbose
        self.chain_df = pd.DataFrame()
        self.counts_df = pd.DataFrame()
        self.stateSpace_type = None
        self.markovChain =  common.MarkovChain(state_size)
        self.name = None
        self.format = None
        self.source = source  # file input source
        
    def __repr__(self, *args, **kwargs):
        return "Collector"

    def collect(self):
        """
        Run collection using the set parameters
        Returns MarkovChain result
        Override this in derived classes
        """
        return None
    
