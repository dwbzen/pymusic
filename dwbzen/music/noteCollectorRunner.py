
#
# ------------------------------------------------------------------------------
# Name:          noteCollectorRunner.py
# Purpose:       Run NoteCollector
#
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from common.collector import Collector
from music.noteCollector import NoteCollector
import argparse

class NoteCollectorRunner(Collector):
    """ Executes NoteRunner with the parameters provided in the command line
    
    """
    
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument("--order", "-o", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-s", "--source", help="input file (.mxl or .musicxml), folder name, or composer name ('bach' for example)")
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        parser.add_argument("-n","--name", help="Name of resulting MarkovChain, used to save to file", type=str)
        parser.add_argument("-f","--format", help="Save output format. Default is csv", type=str, choices=['csv','json','xlsx'], default='csv' )
        parser.add_argument("--sort", help="Sort resulting MarkovChain ascending on both axes", action="store_true", default=False)
        parser.add_argument("-d","--display", help="display resulting MarkovChain in json or cvs format",type=str, choices=['csv','json','chain'] )
        parser.add_argument("-p","--parts", help="part name(s) or number(s) to include in building the MarkovChain", type=str)
        parser.add_argument("-m", "--mode", \
            help="Notes collection mode: ap (absolute pitch), dp (diatonic pitch), apc (absolute pitch class), dpc (diatonic pitch class) sd (scale degree)", \
                            type=str, choices=['ap','dp', 'apc','dpc', 'sd' ], default='dpc')
        parser.add_argument("--enforceRange", "-e", help="Enforce ranges of selected instruments, applies to diatonic collection modes.", action="store_true", default=False)
        parser.add_argument("--show", help="Show the original or transposed score when collection is complete. Does not apply when source is multiple scores.", \
                            type=str, choices=['original', 'transposed', 'none'], default='none')
        parser.add_argument("--filter", help="Apply filter to parts", type=str, default=None)
        parser.add_argument("--keypart", help="Part that determines the overall score Key", type=str, default=None)

        args = parser.parse_args()
        if args.verbose > 0:
            print('run NoteCollector')
            print(args)

        collector = NoteCollector(state_size = args.order, verbose=args.verbose, source=args.source, parts=args.parts, \
                                        collection_mode=args.mode, enforce_range=args.enforceRange )
        collector.name = args.name
        collector.format = args.format
        collector.sort_chain = args.sort
        collector.set_score_filter(args.filter)    # could be None
        collector.key_partName = args.keypart      # could be None
        #
        # only for Bach works in the music21 corpus
        #
        collector.key_partName = 'Soprano'
        
        if args.verbose > 0:
            print(collector.__str__())

        
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
                
        nscores = collector.number_of_scores
        if args.show != 'none' and nscores==1:
            theScore = collector.score
            if args.show == 'transposed':
                theScore = collector.transposed_score
            elif args.show == 'original':
                theScore = collector.score
                
            if theScore is not None:
                theScore.show()


