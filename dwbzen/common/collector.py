
# ------------------------------------------------------------------------------
# Name:          collector.py
# Purpose:       Base collector class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import pandas as pd
from .markovChain import MarkovChain
from .utils import Utils
from .collectorProducer import CollectorProducer

class Collector(CollectorProducer):
    """Collects data from a defined source and builds a MarkovChain of a given order.
    
        Collector subclasses are tailored to the specific data type being collected and how that data is sourced.
        A collector has a corresponding Producer class that takes
        a MarkovChain as input and produces data.
        For example, a CharacterCollector creates a MarkovChain
        from a word stream (strings). The WordProducer reverses the process.
        
        The terminal_object and initial_object must be set appropriately
        by derived (concrete) classes. 
        terminal_object should be set to a value that does not occur
        in the collection source data. For example, CharacterCollector
        sets the value to '~'. IntervalCollector sets the value to
        a interval.Interval to interval.Interval(99).
        The initial_object represents the start of whatever unit is being collected
        This is used to identify an initial seed
    """
    
    def __init__(self, state_size, verbose=0, source=None, domain='text'):
        """Initialize elements common to all Collector subclasses.
        
        The chain_df and counts_df DataFrames index and columns are set by the subclass 
        and is totally dependent on the target domain (for example 'text') and units (for example, characters or words)
        """
        super().__init__(state_size, verbose=verbose, source=source, domain=domain)
        
        self.stateSpace_type = None
        self.markovChain =  None

        self.sort_chain = True

        self.terminal_object = None         # must be set in derived classes
        self.initial_object = None          # must be set in derived classes
        
        self._initial_keys_df = None     # DataFrame created by collect() from counts_df
        self._initial_keys = None        # unique list of key values of initial_keys_df
        self._keys = None                # unique key values of counts_df
        
    def __repr__(self, *args, **kwargs):
        return "Collector"
    
     
    def get_initial_keys(self):
        return self._initial_keys
    
    def get_keys(self):
        return self._keys
           
           
    def _add_counts_to_model(self, model: dict, countsdf: pd.DataFrame, akey: str):
        key_df = countsdf[countsdf['key'] ==  akey]
        s = (key_df['count']/key_df['count'].sum()).cumsum()
        model[akey] = key_df.assign(prob=s )

            
    def _create_chain(self, initial=True) -> MarkovChain:
        """Creates a MarkovChain instance from a counts_df DataFrame
        
        The MarkovChain model is chain_df DataFrame with the columns: key, word, count (from count_df) and prob (the probability)
        'key' is a string of n-words/characters (n=order of the chain) that appear in the source,
        'word' is the next token, and 'prob' is the probability that combination appears in the source.
        The probabilities are computed from the counts.
        
        Parameters:
            initial - if True (the default) create the MarkovChain from initial_keys only
        """

        thekeys = self._initial_keys
        if not initial:
            thekeys = self._keys
        
        self.markovChain = MarkovChain(self.order, self.counts_df, keys=thekeys, chain_df=None,  myname=self.name)
        if self.sort_chain:
            self.chain_df = self.markovChain.chain_df.sort_values(by=['key','word'], ignore_index=True, inplace=False)
            self.markovChain.chain_df = self.chain_df
        
        return self.markovChain
    
    def run(self):
        """Invokes the derived class's collect() function and invokes save()
        
        Invokes the derived class's collect() function and if the resulting
        MarkovChain is valid, invokes save()
        Returns the boolean results of the collect() and save() as a dict()
        with keys 'collect_result' and 'save_result'
        """
        
        save_result = False
        collect_result = False
        self.collect()
        if self.verbose > 1:
            print(f" Counts:\n {self.counts_df}")
            print(f" MarkovChain:\n {self.markovChain}")
            if self.verbose > 2:
                print(self.markovChain.__repr__())        
        
        if self.markovChain is not None and len(self.markovChain.chain_df) > 0:
            collect_result = True
            save_result = self.save()
            
        return {'collect_result' : collect_result, 'save_result' : save_result}

    def collect(self):
        """
        Override in subclass
        """
        return None

    def save(self):
        save_result = super().save()
        return save_result
    
    def get_json_output(self):
        return Utils.get_json_output(self.chain_df)

if __name__ == '__main__':
    print(Collector.__doc__)
        
