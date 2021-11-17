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

from .characterCollector import CharacterCollector
from .markovChain import MarkovChain
from .utils import Utils
from .wordProducer import WordProducer
import argparse
import sys
import pandas as pd

class WordProducerRunner(object):
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        #
        # Collector arguments
        #
        parser.add_argument("order", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-t", "--text", help="in-line text input. One of --text or --source must be specified")
        parser.add_argument("-s", "--source", help="input file name")
        parser.add_argument("-i","--ignoreCase", help="ignore input case", action="store_true", default=False)

        #
        # Producer arguments
        #
        parser.add_argument("-c", "--chainFile", help="Existing serialized MarkovChain file (json), or POS file name .",  type=str, default=None)
        parser.add_argument('outfile', nargs='?', help="Optional output file name", type=argparse.FileType('w'), default=sys.stdout)

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
        if args.verbose > 0:
            print('run WordProducer')
            print(args)
        if args.chainFile is None and not (args.source is None and args.text is None):   # run the collector first
            source_file = args.source
            collector = CharacterCollector(state_size = args.order, verbose=args.verbose, source=source_file, text=args.text, ignoreCase=args.ignoreCase)
            collector.sort_chain = True
            markovChain = collector.collect()
        else:
            # use serialized MarkovChain file in JSON format (--chain )as input
            file_info = Utils.get_file_info(args.chainFile)
            thepath = file_info["path_text"]
            ext = file_info['extension'].lower()
            if args.verbose > 0:
                print(file_info)
            if not file_info['exists']:
                print(f"{thepath} does not exist")
                exit()
            else:
                if ext=='json':
                    mc_df = pd.read_json(thepath, orient="index")
                    markovChain = MarkovChain(order, chain_df=mc_df)
                elif ext=='pos':     # parts-of-speech file  TODO
                    pass

        #
        # markovChain will never, ever be None
        #
        wordProducer = WordProducer(order, markovChain, source_file, args.min, args.max, args.num, args.verbose )
        if args.chainFile is not None:
            wordProducer.chain_file = args.chainFile
        wordProducer.initial = args.initial
        wordProducer.seed = args.seed
        wordProducer.recycle_seed_count = args.recycle
        words = wordProducer.produce()
        # print(words)
            
