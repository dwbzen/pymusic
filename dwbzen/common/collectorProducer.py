# ------------------------------------------------------------------------------
# Name:          collectorProducer.py
# Purpose:       Base class for Collector and Producer.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import pandas as pd
from .markovChain import MarkovChain
from .utils import Utils
from .environment import Environment

class CollectorProducer(object):
    
    def __init__(self, state_size=2, verbose=0, source=None, domain='text'):
        
        self.order = state_size
        self.domain = domain
        self.verbose = verbose
        self.source = source    # file input or DataFrame source
        self.name = None        # set by the user on the command line
        self.format = None      # csv or json
        
        self.chain_filename = None          # MarkovChain.chain_df filename
        self.counts_filename = None         # MarkovChain.counts_df filename
        
        self.chain_df = None        # pd.DataFrame()
        self.counts_df = None       # pd.DataFrame()
        #
        # update to reflect your environment
        #
        env = Environment.get_environment()
        self.save_folder = env.get_resource_folder(domain)   # for example "/Compile/dwbzen/resources/text"
        
        self.chainFileName = '_chain'       # appended to self.name for the MarkovChain file
        self.countsFileName = '_counts'     # appended to self.name for the counts file
        
        
    def __repr__(self):
        return f"CollectorProducer {self.order}"

    
    def save(self):
        """Saves the MarkovChain and counts DataFrame files
        
        The chain_df DataFrame of the MarkovChain is saved in the specified format,
        csv, Excel or json, to the self.save_folder directory.
        The filename is the name of the MarkovChain (self.name) + the chainFileName.
        The chainFileName default is '_chain' and this is typically set
        to something more appropriate in Collector subclasses.
        For example, '_charsChain'.
        
        Similarly, the counts_df DataFrame is saved using the self.countsFileName
        to create the save filename. For example, '_charsCounts'
        
        """
        save_result = False
        if self.name is not None:   # format will always be set to something, even if name is None
            self.markovChain.name = self.name
            
            self.filename = "{}/{}{}.{}".format(self.save_folder, self.name, self.chainFileName, self.format)
            self.counts_file = "{}/{}{}.{}".format(self.save_folder, self.name, self.countsFileName, self.format)
            if self.verbose > 1:
                print(f"output filename '{self.filename}' counts: {self.counts_file}")
            if len(self.chain_df) > 0:
                if self.format == 'csv':
                    self.chain_df.to_csv(self.filename)
                    self.counts_df.to_csv(self.counts_file)
                elif self.format == 'json':
                    dumped = Utils.get_json_output(self.chain_df)
                    with open(self.filename, 'w') as f:
                        f.write(str(dumped))
                    with open(self.counts_file, 'w') as f:
                        f.write(str(Utils.get_json_output(self.counts_df)))
                else: # must be excel
                    self.chain_df.to_excel(self.filename, sheet_name='Sheet 1',index=False)
                    self.counts_df.to_excel(self.counts_file, sheet_name='Sheet 1',index=False)
                save_result = True
            else:
                save_result = False
                if self.verbose > 0:
                    print("Empty MarkovChain")
        return save_result
    