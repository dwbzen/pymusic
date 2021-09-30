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
#                The terminal_object and initial_object must be set appropriately
#                by derived (concrete) classes. 
#                terminal_object should be set to a value that does not occur
#                in the collection source data. For example, CharacterCollector
#                sets the value to '~'. IntervalCollector sets the value to
#                a interval.Interval to interval.Interval(99).
#                initial_object represents the start of whatever unit is being collected
#                This is used to identify an initial seed.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright � 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import pandas as pd
import common
import json

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
        self.sort_chain = False
        self.save_folder="/Compile/dwbzen/resources"
        self.filename = None
        self.counts_file = None
        self.terminal_object = None         # must be set in derived classes
        self.initial_object = None          # must be set in derived classes
        
    def __repr__(self, *args, **kwargs):
        return "Collector"

    def run(self):
        """
        Invokes the derived class's collect() function and if the resulting
        MarkovChain is valid, invokes save() 
        Returns the boolean results of the collect() and save() as a dict()
        with keys collect_result and save_result
        """
        save_result = False
        collect_result = False
        self.collect()
        if self.markovChain is not None and len(self.markovChain.chain_df) > 0:
            collect_result = True
            save_result = self.save()
        return {'collect_result' : collect_result, 'save_result' : save_result}

    def collect(self):
        """
        Override in derived classes
        """
        return None
    
    def get_json_output(self):
        result = self.chain_df.to_json(orient='index')
        parsed = json.loads(result)
        return json.dumps(parsed, indent=4)
    
    def save(self):
        save_result = True
        if self.name is not None:   # format will always be set to something, even if name is None
            self.markovChain.name = self.name
            
            self.filename = "{}/{}.{}".format(self.save_folder, self.name, self.format)
            self.counts_file = "{}/{}_counts.{}".format(self.save_folder, self.name, self.format)
            if self.verbose > 1:
                print(f"output filename '{self.filename}' counts: {self.counts_file}")
            if len(self.chain_df) > 0:
                if self.format == 'csv':
                    self.chain_df.to_csv(self.filename)
                    self.counts_df.to_csv(self.counts_file)
                elif self.format == 'json':
                    dumped = self.get_json_output()
                    with open(self.filename, 'w') as f:
                        f.write(str(dumped))
                    self.counts_df.to_json(self.counts_file, orient='index')
                else: # must be excel
                    self.chain_df.to_excel(self.filename, sheet_name='Sheet 1',index=False)
                    self.counts_df.to_excel(self.counts_file, sheet_name='Sheet 1',index=False)
            else:
                save_result = False
                if self.verbose > 0:
                    print("Empty MarkovChain")
        return save_result
