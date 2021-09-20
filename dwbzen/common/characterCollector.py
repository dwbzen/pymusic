# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:          characterCollector.py
# Purpose:       Character collector class.
#
#                CharacterCollector creates a MarkovChain
#                from a word stream (strings). The corresponding
#                Producer class is WordProducer which reverses the process.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright � 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import common
import argparse
import pandas as pd

class CharacterCollector(common.Collector):

    def __init__(self, state_size=2, verbose=False, source=None, text=None, ignoreCase=False):
        super().__init__(state_size, verbose, source)
        self.text = text
        self.ignoreCase = ignoreCase
        self.my_index = []
        self.my_columns = []
        # a list of dict objects, each one a dict where 
        # the key is the index and the value is a list of counts for each my_column
        #
        self.stats = []

    def __repr__(self):
        return f"CharacterCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}, text={self.text}, ignoreCase={self.ignoreCase}"
    
    def process(self, line):
        line = line.replace('\n',' ')
        
        #
        #
        if self.ignoreCase:
            line = line.lower()
        line_len = len(line)
        ind = 0         # index of current character
        more = line_len > self.order    # more to go?
        while more:
            index_str = line[ind:ind+self.order]
            col_str = line[ind+self.order]
            if self.verbose:
                print(f"token {index_str}  char '{col_str}'")
            #
            # add the token index_str and the character that follows, col_str,
            # to the index and column list respectively
            # These will be the index= and columns= of the MarkovChain DataFrame
            #
            if len(self.counts) == 0:
                # initialize the MarkovChain
                self.counts = pd.DataFrame(data=[1],index=[index_str], columns=[col_str])
                self.my_index.append(index_str)
                self.my_columns.append(col_str)
            else:
                if index_str not in self.counts.index:   # add a new row
                    self.counts.loc[index_str, col_str] = 1
                    self.my_index.append(index_str)
                    if col_str not in self.my_columns:
                        self.my_columns.append(col_str)
                
                else:  # update existing index
                    if col_str in self.counts.columns:
                        self.counts.loc[index_str, col_str] = 1 + self.counts.loc[index_str, col_str]
                    else:
                        self.counts.loc[index_str, col_str] = 1
                        self.my_columns.append(col_str)
                        
            ind = ind + 1
            more = line_len > (ind + self.order)
            
        self.counts = self.counts.fillna(0)
        #
        # create probabilities from counts
        #
        
        print("process line complete")
        
    
    def collect(self):
        """
        Run collection using the set parameters
        Returns MarkovChain result as a DataFrame
        """
        if self.source is not None:
            with open(self.source, "r") as f:
                lnum = 1
                for line in f:
                    if self.verbose:
                        print(f"line {lnum}\t{line}", end='')
                    line = ' ' + line.strip() + ' '     # add intial and terminal characters (a space)
                    self.process(line)
                    lnum = lnum + 1
        elif self.text is not None:
            # add a terminal character (a space) if needed
            txt = self.text.strip() + ' '
            self.process(txt)
        if self.verbose:
            print(self.chain)
        
    def save(self):
        if self.name is not None:   # format will always be set
            filename = "{}.{}".format(self.name, self.format)
            if self.verbose:
                print(f"output filename {filename}")
            if len(self.chain) > 0:
                if self.format == 'csv':
                    self.chain.to_csv(filename)
                elif self.format == 'json':
                    self.chain.to_json(filename, orient='index')
                else: # must be excel
                    self.chain.to_excel(filename, sheet_name='First_Sheet',index=False)
                if self.verbose:
                    print(f"MarkovChain written to file: {filename}")
            else:
                if self.verbose:
                    print("Empty MarkovChain")
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument("order", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-t", "--text", help="in-line text input. One of --text or --source must be specified")
        parser.add_argument("-s", "--source", help="input file name")
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="store_true")
        parser.add_argument("-i","--ignoreCase", help="ignore input case", action="store_true")
        parser.add_argument("-n","--name", help="Name of resulting MarkovChain, used to save to file", type=str)
        parser.add_argument("-f","--format", help="Output format. Default is csv", type=str, choices=['csv','json','xlsx'], default='csv' )
        args = parser.parse_args()
        if args.verbose:
            print('run CharacterCollector')
            print(args)
            
        collector = common.CharacterCollector(state_size = args.order, verbose=args.verbose, source=args.source, text=args.text, ignoreCase=args.ignoreCase)
        collector.name = args.name
        collector.format = args.format
        if args.verbose:
            print(collector.__repr__())
        
        chain = collector.collect()
        collector.save()

