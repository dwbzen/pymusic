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

import random
import pandas as pd
from .environment import Environment

class Producer(object):
    
    def __init__(self, state_size, markovChain, source_file=None, min_size=0, max_size=0, num=20, verbose=0, domain='text', rand_seed=None):
        self.markovChain = markovChain        # a MarkovChain instance, provided by a ProducerRunner
        self.order = state_size
        self.domain = domain
        self.min_size = min_size
        self.max_size = max_size
        self.num = num      # units defined in Producer subclass
        self.name = None
        self.source_file = source_file  # file input source
        self.verbose=verbose
        
        self.output_format = None
        self.outfile=None
        self.seed=None
        self.sort=None
        self.chain_file = None          # serialized MarkovChain.chain_df json file
        self.initial=True
        self.chain_df = self.markovChain.chain_df
        self.keys = pd.Series(self.chain_df.index)
        #
        # count of how many times the current seed has been used
        # when >= self.recycle_seed_count, a new seed is picked
        self.seed_count = 0
        self.recycle_seed_count = 1     # pick a new seed every n things produced
        #
        # update to reflect your environment
        #
        env = Environment.get_environment()
        self.save_folder = env.get_resource_folder(domain)   # for example "/Compile/dwbzen/resources/text"

        random.seed(a=rand_seed)
        
        
    def __repr__(self):
        return f"Producer {self.order}"
    
    def get_seed(self):  # override in derived class
        return None
    
    def get_next_seed(self):
        """Checks the seed_count against the recycle_seed_count and if >= gets a new seed, otherwise returns the existing one
        
        """
        self.seed_count = self.seed_count + 1
        aseed = self.seed
        if self.seed_count >= self.recycle_seed_count or aseed is None:
            # pick a new seed
            aseed = self.get_seed()
            self.seed_count = 0
            self.seed = aseed
        return aseed
    
    def produce(self):
        """
        Run the Producer with the parameters provided
        Returns a list of whatever the specific Producer is, well, producing (str for example)
        Override this in derived classes
        """
        return None


