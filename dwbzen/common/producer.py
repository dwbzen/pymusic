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


class Producer(object):
    
    def __init__(self, state_size, markovChain=None, source_file=None, min_size=0, max_size=0, num=10, verbose=0):
        self.markovChain = markovChain        # a MarkovChain instance
        self.order = state_size
        self.min_size = min_size
        self.max_size = max_size
        self.output_format = None
        self.source_file = source_file  # file input source
        self.chain_file = None          # serialized MarkovChain.chain_df json file
        self.num = num
        self.initial=False
        self.verbose=verbose
        self.recycle_seed_count = 1     # pick a new seed every n things produced
        
    def __repr__(self):
        return f"Producer {self.order}"
    
    def get_seed(self):  # override in derived class
        return None
    
    def produce(self):
        """
        Run the Producer with the parameters provided
        Returns a list of whatever the specific Producer is, well, producing (str for example)
        Override this in derived classes
        """
        return None


