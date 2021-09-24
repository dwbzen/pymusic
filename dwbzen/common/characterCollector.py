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
import json

class CharacterCollector(common.Collector):

    def __init__(self, state_size=2, verbose=0, source=None, text=None, ignoreCase=False):
        super().__init__(state_size, verbose, source)
        self.text = text
        self.ignoreCase = ignoreCase
        self.terminal_character = '~'
        self.initial_character = ' '
        self.sort_chain = False
        self.markovChain.collector = CharacterCollector
        self.save_folder="/Compile/dwbzen/resources"

    def __str__(self):
        return f"CharacterCollector order={self.order} verbose={self.verbose} name={self.name} format={self.format}, source={self.source}, text={self.text}, ignoreCase={self.ignoreCase}"
    
    def process(self, line):
        line = line.replace('\n', self.terminal_character)
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
            if self.verbose >= 2:
                print(f"token {index_str}  char '{col_str}'")
            #
            # add the token index_str and the character that follows, col_str,
            # to the index and column list respectively
            # These will be the index= and columns= of the MarkovChain DataFrame
            #
            if len(self.counts_df) == 0:
                # initialize the MarkovChain
                self.counts_df = pd.DataFrame(data=[1],index=[index_str], columns=[col_str])

            else:
                if index_str not in self.counts_df.index:   # add a new row
                    self.counts_df.loc[index_str, col_str] = 1
                
                else:  # update existing index
                    if col_str in self.counts_df.columns:
                        self.counts_df.loc[index_str, col_str] = 1 + self.counts_df.loc[index_str, col_str]
                    else:
                        self.counts_df.loc[index_str, col_str] = 1
                        
            self.counts_df = self.counts_df.fillna(0)
            ind = ind + 1
            more = line_len > (ind + self.order)
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
                    if self.verbose > 0:
                        print(f"line {lnum}\t{line}", end='')
                    line = self.initial_character + line.strip() + self.terminal_character     # add intial and terminal characters (typically a space)
                    self.process(line)
                    lnum = lnum + 1
        elif self.text is not None:
            # add initial and terminal characters if needed
            txt = self.initial_character + self.text.strip() + self.terminal_character
            self.process(txt)
        self.counts_df.rename_axis('KEY', inplace=True)
        if self.sort_chain:
            self.counts_df.sort_index('index', ascending=True, inplace=True)
            self.counts_df.sort_index(axis=1, ascending=True, inplace=True)
        #
        # create the MarkovChain from the counts by added probabilities
        #
        sums = self.counts_df.sum(axis=1)
        self.chain_df = self.counts_df.div(sums, axis=0)
        self.chain_df.rename_axis('KEY', inplace=True)
        self.markovChain.chain_df = self.chain_df
        if self.verbose > 1:
            print(f" Counts:\n {self.counts_df}")
            print(f" MarkovChain:\n {self.markovChain}")
            if self.verbose > 1:
                print(self.markovChain.__repr__())
        
        return self.markovChain
        
    def save(self):
        if self.name is not None:   # format will always be set
            self.markovChain.name = self.name
            
            filename = "{}/{}.{}".format(self.save_folder, self.name, self.format)
            counts_file = "{}/{}_counts.{}".format(self.save_folder, self.name, self.format)
            if self.verbose > 0:
                print(f"output filename '{filename}' counts: {counts_file}")
            if len(self.chain_df) > 0:
                if self.format == 'csv':
                    self.chain_df.to_csv(filename)
                    self.counts_df.to_csv(counts_file)
                elif self.format == 'json':
                    result = self.chain_df.to_json(orient='index')
                    parsed = json.loads(result)
                    dumped = json.dumps(parsed, indent=4)
                    with open(filename, 'w') as f:
                        f.write(str(dumped))
                    self.counts_df.to_json(counts_file, orient='index')
                else: # must be excel
                    self.chain_df.to_excel(filename, sheet_name='Sheet 1',index=False)
                    self.counts_df.to_excel(counts_file, sheet_name='Sheet 1',index=False)
                if self.verbose > 0:
                    print(f"MarkovChain written to file: {filename}")
            else:
                if self.verbose > 0:
                    print("Empty MarkovChain")
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument("order", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-t", "--text", help="in-line text input. One of --text or --source must be specified")
        parser.add_argument("-s", "--source", help="input file name")
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count")
        parser.add_argument("-i","--ignoreCase", help="ignore input case", action="store_true", default=False)
        parser.add_argument("-n","--name", help="Name of resulting MarkovChain, used to save to file", type=str)
        parser.add_argument("-f","--format", help="Output format. Default is csv", type=str, choices=['csv','json','xlsx'], default='csv' )
        parser.add_argument("--sort", help="Sort resulting MarkovChain ascending on both axes", action="store_true", default=False)
        args = parser.parse_args()
        if args.verbose > 0:
            print('run CharacterCollector')
            print(args)
            
        collector = common.CharacterCollector(state_size = args.order, verbose=args.verbose, source=args.source, text=args.text, ignoreCase=args.ignoreCase)
        collector.name = args.name
        collector.format = args.format
        collector.sort_chain = args.sort
        if args.verbose > 0:
            print(collector.__repr__())
        chain = collector.collect()
        collector.save()

