#
# ------------------------------------------------------------------------------
# Name:          characterCollector.py
# Purpose:       Executes the CharacterCollector
#
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from .collector import Collector
from .characterCollector import CharacterCollector
import argparse

class CharacterCollectorRunner(Collector):
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument("order", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-t", "--text", help="in-line text input. One of --text or --source must be specified")
        parser.add_argument("-s", "--source", help="input file name")
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        parser.add_argument("-i","--ignoreCase", help="ignore input case", action="store_true", default=False)
        parser.add_argument("-n","--name", help="Name of resulting MarkovChain, used to save to file", type=str)
        parser.add_argument("-f","--format", help="Save output format. Default is csv", type=str, choices=['csv','json','xlsx'], default='csv' )
        parser.add_argument("--sort", help="Sort resulting MarkovChain ascending on both axes", action="store_true", default=False)
        parser.add_argument("-d","--display", help="display resulting MarkovChain in json or cvs format",type=str, choices=['csv','json','chain'] )
        args = parser.parse_args()
        if args.verbose > 0:
            print('run CharacterCollector')
            print(args)
            
        collector = CharacterCollector(state_size = args.order, verbose=args.verbose, source=args.source, text=args.text, ignoreCase=args.ignoreCase)
        collector.name = args.name
        collector.format = args.format
        collector.sort_chain = args.sort
        if args.verbose > 0:
            print(collector.__repr__())
        run_results = collector.run()
        if run_results['save_result']:
            print(f"MarkovChain written to file: {collector.filename}")
        if args.display is not None:
            # display in specified format
            if args.display=='json':
                print(collector.get_json_output())
            elif args.display=='csv':
                print(collector.markovChain.chain_df.to_csv(line_terminator='\n'))
            else:   # assume 'chain' and display the data frame
                print(collector.markovChain.chain_df)
