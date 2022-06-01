# ------------------------------------------------------------------------------
# Name:          collectorProducer.py
# Purpose:       Base class for Collector and Producer.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from .utils import Utils
from .environment import Environment
import sys
import pandas as pd

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
        # update Environment to reflect your environment
        #
        env = Environment.get_environment()
        self.save_folder = env.get_resource_folder(domain)   # for example "/Compile/dwbzen/resources/text"
        
        self.chainFileName = '_chain'       # appended to self.name for the MarkovChain file
        self.countsFileName = '_counts'     # appended to self.name for the counts file
        
        
    def __repr__(self):
        return f"CollectorProducer {self.order}"

    @staticmethod
    def save_df(df:pd.DataFrame, filename, file_format, orient='index', sheet_name='Sheet 1'):
        result = True
        if file_format=='csv':
            df.to_csv(filename)
        elif file_format=='json':
            dumped = Utils.get_json_output(df, orient)
            with open(filename, 'w') as f:
                f.write(str(dumped))
        elif file_format=='xlsx' or file_format=='excel':
            df.to_excel(filename, sheet_name=sheet_name, index=False)
        else:
            result = False
            print("Empty DataFrame(s)", sys.stderr)
        return result
    
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
                print(f"output filenames '{self.filename}' counts: {self.counts_file}")
            save_result = CollectorProducer.save_df(self.chain_df, self.filename, self.format)
            save_result = save_result and CollectorProducer.save_df(self.counts_df, self.counts_file, self.format)
            
        return save_result
    