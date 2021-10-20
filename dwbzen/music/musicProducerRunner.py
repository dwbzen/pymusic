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

import music
import common
import argparse
import sys
import pandas as pd

class MusicProducerRunner(object):
    
    if __name__ == '__main__':
        """Produce a Score from MarkovChain
        
        input format for chain files is 
         --chainFiles 'notes=bwv29_8_notesChain.json,durations=bwv29_8_durationsChain.json'
        or
         --chainFiles 'intervals=bwv29_8_intervalsChain.json,durations=bwv29_8_durationsChain.json'
        
        The seed format depends on the source - Notes or Intervals
        For intervals, specify semitones, for example --seed "5,-2"
        For notes, specify the note with the octave, for example --seed "C#4,B3"
     
        """
        
        parser = argparse.ArgumentParser(description="Produce a Music21 Score from a new or existing MusicCollector MarkovChain")
        #
        # Collector arguments
        #
        parser.add_argument("order", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-s", "--source", help="input file (.mxl or .musicxml), folder name, or composer name ('bach' for example)", default=None)
        parser.add_argument("-t", "--type", help="Source object type: note or interval", type=str, choices=['note','interval'], default='interval')
        parser.add_argument("-p","--parts", help="part name(s) or number(s) to include in building the MarkovChain", type=str, default=None)
        parser.add_argument("-f","--format", help="Save output format. Default is json", type=str, choices=['csv','json','xlsx'], default='json' )
        parser.add_argument("--sort", help="Sort resulting MarkovChain ascending on both axes", action="store_true", default=False)
        #
        # Producer arguments
        #
        parser.add_argument("-c", "--chainFiles", help="Existing serialized MarkovChain and Durations files (json).",  type=str, default=None)
        parser.add_argument("--show", help="How to display resulting score", type=str, choices=['text','musicxml','midi'], default='musicxml')
        parser.add_argument("--name", help="Name of resulting score, used to save to .musicxml file", type=str, default=None)
        parser.add_argument("-n", "--num", help="Total number of notes per part to produce",  type=int, default=20)
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        parser.add_argument("--seed", help="Initial seed, length must be equal to the order of source chain", type=str, default=None)
        parser.add_argument("--produce", help="Comma-delimited list of Part name(s) to produce", type=str, default='part')
        parser.add_argument("--initial", help="choose initial seed only", action="store_true", default=False)
        parser.add_argument("--recycle", help="How often to pick a new seed, default is pick a new seed after each measure produced", type=int, default=1)
        args = parser.parse_args()
        markovChain = None
        if args.verbose > 0:
            print('run ScoreProducer')
            print(args)
        randomseed = music.Utils.get_timedelta()
        durations_chain = None
        markovChain = None
        
        if args.chainFiles is None and args.source is not None:
            #
            # run the collector first to produce the MarkovChain
            #
            if args.type == 'note':
                collector = music.NoteCollector(state_size = args.order, verbose=args.verbose, source=args.source, parts=args.parts )
            elif args.type == 'interval':
                collector = music.IntervalCollector(state_size = args.order, verbose=args.verbose, source=args.source, parts=args.parts )
            
            collector.name = args.name
            collector.format = args.format
            collector.sort_chain = args.sort
            run_results = collector.run()
            if run_results['save_result']:
                print(f"MarkovChain written to file: {collector.filename}")
            markovChain = collector.markovChain
            durations_chain = collector.durationCollector.markovChain
        else:
            # use serialized MarkovChain and Durations files in JSON format as input
            file_list = args.chainFiles.split(',')  # chain file,durations file
            if len(file_list) != 2:
                raise TypeError('A MarkovChain file and Durations file must both be specified')
            i = 0
            for chainFile in file_list:
                file_info = common.Utils.get_file_info(chainFile)
                thepath = file_info["path_text"]
                ext = file_info['extension'].lower()
                if args.verbose > 0:
                    print(file_info)
                if not file_info['Path'].exists():
                    print(f"{thepath} does not exist")
                    exit()
                else:
                    if ext=='json':
                        mc_df = pd.read_json(thepath, orient="index")
                        if i==0:
                            markovChain = common.MarkovChain(args.order, chain_df=mc_df)
                            i=i+1
                        else:
                            durations_df = mc_df
                    else:
                        raise TypeError('MarkovChain file type must be json')
        
        musicProducer = music.MusicProducer(args.order, markovChain, args.source, args.parts, args.produce, num=args.num, verbose=args.verbose, rand_seed=randomseed, producerType=args.type)
        musicProducer.show = args.show
        musicProducer.name = args.name
        musicProducer.recycle_seed_count = args.recycle
        musicProducer.initial = args.initial
        musicProducer.durations_chain = durations_chain
        
        theScore = musicProducer.produce()
        if theScore is not None:
            theScore.show(args.show)
            
