# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       Runs CharacterCollector if needed and then WordProducer
#
#
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from common.characterCollector import CharacterCollector
from common.utils import Utils
from common.markovChain import MarkovChain
from common.wordProducer import WordProducer
import pandas as pd
import argparse

class WordProducerRunner(object):
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        #
        # CharacterCollector arguments
        #
        parser.add_argument("order", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-t", "--text", help="in-line text input. One of --text or --source must be specified")
        parser.add_argument("-s", "--source", help="input file name")
        parser.add_argument("-i","--ignoreCase", help="ignore input case", action="store_true", default=False)
        parser.add_argument("--name", help="Name of resulting MarkovChain, used to save to file", type=str, default="mychain")

        #
        # WordProducer arguments
        #
        parser.add_argument("-c", "--chainfile", help="Existing serialized MarkovChain file, or POS file name.",  type=str, default=None)
        parser.add_argument("-f","--format", help="File input/output format. Default is csv", type=str, choices=['csv','json','xlsx'], default='csv' )

        parser.add_argument("-n", "--num", help="Number of words to produce",  type=int, default=10)
        parser.add_argument("--min", help="Minimum length of words", type=int, choices=range(2,6), default=4)
        parser.add_argument("--max", help="Maximum length of words", type=int, choices=range(3,20), default=10)
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        parser.add_argument("--seed", help="Initial seed, length must be equal to the order of source chain", default=None)
        parser.add_argument("--sort", help="Sort the output in Ascending (A) or Decending (D) order", default=None)
        parser.add_argument("-l", "--list", help="Display produce Words in order produced, default is false", action="store_true",default=False)
        parser.add_argument("-p", "--postprocessing", help="post-processing: TC = title case, UC = upper case, LC = lower case. Default is None", default=None)
        parser.add_argument("--initial", help="choose initial seed only (start of word)", action="store_true", default=False)
        parser.add_argument("--pos", help="Source is a part-of-speech file", action="store_true",default=False)
        parser.add_argument("--recycle", help="How often to pick a new seed, default is pick a new seed after each word produced", type=int, default=1)
        args = parser.parse_args()
        
        markovChain = None
        order = args.order
        source_file = None
        chain_filename = None
        counts_filename = None
        if args.verbose > 0:
            print('run WordProducer')
            print(args)
        if args.chainfile is None and not (args.source is None and args.text is None):   # run the collector first
            source_file = args.source
            collector = CharacterCollector(state_size = args.order, verbose=args.verbose, source=source_file, text=args.text, ignore_case=args.ignoreCase)
            collector.sort_chain = True
            run_results = collector.run()
            if run_results['save_result']:
                print(f"MarkovChain written to file: {collector.filename}")
            
            markovChain = collector.markovChain
            
        else:
            # use serialized MarkovChain file  and counts file in specified format
            # for example  --chainfile "/Compile/dwbzen/resources/text/drugBrands"
            #
            chain_filename = f'{args.chainfile}_charsChain.{args.format}'
            counts_filename = f'{args.chainfile}_charCounts.{args.format}'
            
            chain_file_info = Utils.get_file_info(chain_filename)
            chain_path = chain_file_info["path_text"]
            
            counts_file_info = Utils.get_file_info(counts_filename)
            counts_path = counts_file_info["path_text"]

            ext = args.format
            if args.verbose > 0:
                print(chain_file_info)
            if not chain_file_info['exists']:
                print(f"{chain_path} does not exist")
                exit()
            else:
                if ext=='json':
                    chain_df = pd.read_json(chain_path, orient="index")
                    counts_df = pd.read_json(counts_path, orient="index")
                    markovChain = MarkovChain(order, counts_df, chain_df=chain_df)
                elif ext=='csv':     # parts-of-speech file  TODO
                    chain_df = pd.read_csv(chain_path, header=0, names=['key','word','count','prob'])
                    counts_df = pd.read_csv(counts_path, header=0, names=['key','word','count'])
                    markovChain = MarkovChain(order, counts_df, chain_df=chain_df)
                elif ext=='xlsx':
                    pass        # TODO

        #
        # markovChain will never, ever be None
        #
        wordProducer = WordProducer(order, markovChain, source_file, args.min, args.max, args.num, args.verbose )
        if chain_filename is not None:
            wordProducer.chain_filename = chain_filename
            wordProducer.counts_filename = counts_filename

        wordProducer.initial = args.initial
        wordProducer.seed = args.seed
        wordProducer.recycle_seed_count = args.recycle
        words = wordProducer.produce()  # also prints the words
        if args.verbose > 1:
            print(words)
            
