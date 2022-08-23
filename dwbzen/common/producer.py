# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       Base Producer class.
#
#
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright 2022 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import random
from common.markovChain import MarkovChain
from common.collectorProducer import CollectorProducer
import pandas as pd

class Producer(CollectorProducer):
    
    def __init__(self, state_size, markovChain:MarkovChain, source=None, min_size=0, max_size=0, num=20, verbose=0, domain='text', rand_seed=None):
        
        super().__init__(state_size, verbose=verbose, source=source, domain=domain)
        
        self.markovChain = markovChain        # a MarkovChain instance, provided by a ProducerRunner
        self.min_size = min_size
        self.max_size = max_size
        self.num = num      # units defined in Producer subclass
        
        self.outfile=None
        self.seed=None
        self.sort=None
        self.initial=True
        self.chain_df = self.markovChain.chain_df
        self.counts_df = self.markovChain.counts_df
        self.chain_updated = False
        
        #
        # initial keys and all keys
        #
        self._initial_keys = None
        self._keys = None
        self._initial_keys_df = None
        self.display_as_produced = False   # display each object (word, sentence etc.)  as it's produced
        #
        # count of how many times the current seed has been used
        # when >= self.recycle_seed_count, a new seed is picked
        self.seed_count = 0
        self.recycle_seed_count = 1     # pick a new seed every n things produced

        random.seed(a=rand_seed)
        
        
    def __repr__(self):
        return f"Producer {self.order}"
    
    def _add_key(self, key):
        key_df = self.counts_df[self.counts_df['key']==key]
        s = (key_df['count']/key_df['count'].sum()).cumsum()
        key_df = key_df.assign(prob=s )
        self.chain_df = pd.concat([self.chain_df, key_df], ignore_index= True)
        self.chain_updated = True   # this will trigger a save
        return key_df
    
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

    def save(self):
        save_result = super().save()
        return save_result
    
