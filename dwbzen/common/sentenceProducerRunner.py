# ------------------------------------------------------------------------------
# Name:          sentenceProducer.py
# Purpose:       Runs WordCollector if needed and then SentenceProducer
#
#
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright 2022 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from common.wordCollector import WordCollector
from common.utils import Utils
from common.markovChain import MarkovChain
from common.sentenceProducer import SentenceProducer
import argparse
import pandas as pd

class SentenceProducerRunner(object):

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        #
        # WordCollector arguments
        #
        parser.add_argument("order", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-t", "--text", help="in-line text input. One of --text or --source must be specified")
        parser.add_argument("-s", "--source", help="input file name")
        parser.add_argument("-i","--ignoreCase", help="ignore input case", action="store_true", default=False)
        parser.add_argument("--name", help="Name of resulting MarkovChain, used to save to file", type=str, default="mychain")
        parser.add_argument("-r", "--remove_stop_words", help="remove common stop words", action="store_true", default=False)
        parser.add_argument("-p", "--processing_mode", help="specify words of sentences", choices=['words','sentences', 'lines'], default='sentences')

        #
        # SentenceProducer arguments
        #
        parser.add_argument("-c", "--chainfile", help="Existing serialized MarkovChain file.",  type=str, default=None)
        parser.add_argument("-f","--format", help="File input/output format. Default is csv", type=str, choices=['csv','json','xlsx'], default='csv' )

        parser.add_argument("-n", "--num", help="Number of sentences to produce",  type=int, default=10)
        parser.add_argument("--min", help="Minimum length of sentences", type=int, choices=range(2,6), default=5)
        parser.add_argument("--max", help="Maximum length of sentences", type=int, choices=range(3,31), default=10)
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        parser.add_argument("--seed", help="Initial seed, length must be equal to the order of source chain", default=None)
        parser.add_argument("--sort", help="Sort the output in Ascending (A) or Decending (D) order", default=None)
        parser.add_argument("-l", "--list", help="Display produce sentences in order produced, default is false", action="store_true",default=False)
        parser.add_argument("--postprocessing", help="post-processing: TC = title case, UC = upper case, LC = lower case. Default is None", default="TC")
        parser.add_argument("--initial", help="choose initial seed only (start of word)", action="store_true", default=True)
        parser.add_argument("--recycle", help="How often to pick a new seed, default is pick a new seed after each sentence", type=int, default=1)
        parser.add_argument("--display", "-d", help="Display each word as it is produced", action="store_true", default=True)
        args = parser.parse_args()
        
        markovChain = None
        order = args.order
        source_file = None
        chain_filename = None
        counts_filename = None        
        display_as_produced = args.display
        if args.chainfile is None and not (args.source is None and args.text is None):   # run the collector first
            if args.verbose > 0:
                print('run WordCollector')
                print(args)
            collector = WordCollector(state_size=args.order, verbose=args.verbose, source=args.source, text=args.text, ignore_case=args.ignoreCase)
            collector.name = args.name
            collector.format = args.format
            collector.processing_mode = args.processing_mode
            if args.verbose > 0:
                print(collector.__repr__())
        
            run_results = collector.run()
            if run_results['save_result']:
                print(f"MarkovChain written to file: {collector.filename}")
            
            markovChain = collector.markovChain

        else:
            # use serialized MarkovChain file  and counts file in specified format
            # for example  --chainfile "/Compile/dwbzen/resources/text/madnessText"
            #
            order_string = '_0{}'.format(order)
            chain_filename = f'{args.chainfile}_wordsChain{order_string}.{args.format}'
            counts_filename = f'{args.chainfile}_wordCounts{order_string}.{args.format}'
            
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
        
        if args.verbose > 0:
            print('run SentenceProducer')

        sentenceProducer = SentenceProducer(order, markovChain, source_file, args.min, args.max, args.num, args.verbose )
        if chain_filename is not None:
            sentenceProducer.chain_filename = chain_filename
            sentenceProducer.counts_filename = counts_filename
    
        sentenceProducer.initial = args.initial
        sentenceProducer.seed = args.seed   # the initial starting seed, could be None
        sentenceProducer.postprocessing = args.postprocessing
        sentenceProducer.recycle_seed_count = args.recycle
        sentenceProducer.display_as_produced = display_as_produced
        sentences = sentenceProducer.produce()
        
        if not display_as_produced:
            for s in sentences: print(f'{s}')

    