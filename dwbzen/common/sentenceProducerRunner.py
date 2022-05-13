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
import sys
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
        parser.add_argument("-f","--format", help="Save output format. Default is csv", type=str, choices=['csv','json','xlsx'], default='csv' )
        parser.add_argument("-d","--display", help="display resulting MarkovChain in json or cvs format",type=str, choices=['csv','json','chain'] ) 
        parser.add_argument("-r", "--remove_stop_words", help="remove common stop words", action="store_true", default=False)
        parser.add_argument("-p", "--processing_mode", help="specify words of sentences", choices=['words','sentences'], default='words')

        #
        # SentenceProducer arguments
        #
        parser.add_argument("-c", "--chainFile", help="Existing serialized MarkovChain file (json), or POS file name .",  type=str, default=None)
        parser.add_argument('outfile', nargs='?', help="Optional output file name", type=argparse.FileType('w'), default=sys.stdout)

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
        args = parser.parse_args()
        markovChain = None
        order = args.order
        source_file = None
        
        
        if args.chainFile is None:
            if args.verbose > 0:
                print('run WordCollector')
                print(args)
            collector = WordCollector(state_size = args.order, verbose=args.verbose, source=args.source, text=args.text, ignore_case=args.ignoreCase)
            collector.name = args.name
            collector.format = args.format
            collector.processing_mode = args.processing_mode
            if args.verbose > 0:
                print(collector.__repr__())
        
            run_results = collector.run()
            if run_results['save_result']:
                print(f"MarkovChain written to file: {collector.filename}")
            
            markovChain = collector.markovChain
            if args.display is not None:
                # display in specified format
                if args.display=='json':
                    print(collector.get_json_output())
                elif args.display=='csv':
                    print(markovChain.chain_df.to_csv(line_terminator='\n'))
                else:   # assume 'chain' and display the data frame
                    print(markovChain.chain_df)

        else:
            # use serialized MarkovChain file in JSON format (--chain )as input
            file_info = Utils.get_file_info(args.chainFile)
            thepath = file_info["path_text"]
            ext = file_info['extension'].lower()
            if args.verbose > 0:
                print(file_info)
            if not file_info['exists']:
                print(f"{thepath} does not exist", file=sys.stderr)
                exit()
            else:
                if ext=='json':
                    mc_df = pd.read_json(thepath, orient="index")
                    markovChain = MarkovChain(order, chain_df=mc_df)
                elif ext=='csv':
                    mc_df = pd.read_csv(thepath)
                    # need to reindex and then drop the KEY column
                    new_index = mc_df['KEY']
                    mc_df.index = new_index.values
                    mc_df.drop(['KEY'], axis=1, inplace=True)
                    markovChain = MarkovChain(order, chain_df=mc_df)
                else:
                    print(f'{ext} is an invalid file type', file=sys.stderr)
                    exit()
        
        if args.verbose > 0:
            print('run SentenceProducer')

        sentenceProducer = SentenceProducer(order, markovChain, source_file, args.min, args.max, args.num, args.verbose )
        if args.chainFile is not None:
            sentenceProducer.chain_file = args.chainFile
        sentenceProducer.initial = args.initial
        sentenceProducer.seed = args.seed   # the initial starting seed, could be None
        sentenceProducer.postprocessing = args.postprocessing
        sentenceProducer.recycle_seed_count = args.recycle
        sentences = sentenceProducer.produce()
        
        print('\n')
        for s in sentences: print(f'{s}')
               
        
    