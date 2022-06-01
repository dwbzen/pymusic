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

from music.musicProducer import MusicProducer
from music.noteCollector import NoteCollector
from music.intervalCollector import IntervalCollector
from music.instruments import Instruments
from common.utils import Utils
from common.markovChain import MarkovChain
from common.environment import Environment

import argparse
import pandas as pd
from music21 import key

class MusicProducerRunner(object):
    
    if __name__ == '__main__':
        """Produce a Score from MarkovChains
        
        Command line arguments:
            --chainFiles :  the name of existing MarkovChain files for intervals/notes and durations
                            By default it constructs the file names as: 
                            name + chainFileName of the associated collector type ('note' or 'interval') + '.json'
                            in the MusicCollector save_folder. For example, '--type interval --chainFiles bwv29_8' resolves
                            to 'bwv29_8_intervalsChain.json' and 'bwv29_8_durationsChain.json'
                            in the "/Compile/dwbzen/resources/music" folder (the default value of save_folder)
            --initial : The MusicCollectors specify an initial_object and a terminal_object. These values
                        are inserted automatically by the collector at the start of a collection unit,
                        in this case a Part. So for example, if the first interval in a Part is 2 (semitones)
                        the MarkovChain state will be interval.Interval(0) + interval.Interval(2)
                        If --initial is True, then when selecting a seed, pick one in the MarkovChain state space
                        that has the initial_object as the first element.
            --seed :    Optional initial seed.  The seed format depends on the source - Notes or Intervals
                        For intervals, specify semitones, for example --seed "5,-2"
                        For notes, specify the note with the octave, for example --seed "C#4,B3"
                        If unspecified, MusicProducer will select one randomly from the MarkovChain
                        depending on the value of --initial
     
        """
        
        parser = argparse.ArgumentParser(description="Produce a Music21 Score from a new or existing MusicCollector MarkovChain")

        #
        # Collector arguments
        #
        parser.add_argument("--order", "-o", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("--source", "-s", help="input file (.mxl or .musicxml), folder name, or composer name ('bach' for example)", default=None)
        parser.add_argument("--type", "-t", help="Source object type: notes or intervals", type=str, choices=['notes','intervals'], default='intervals')
        parser.add_argument("--parts", "-p", help="part name(s) or number(s) to include in building the MarkovChain", type=str, default=None)
        #
        # mode only applies to 'notes' type
        #
        parser.add_argument("--mode", \
                            help="Notes collection mode: ap (absolute pitch), dp (diatonic pitch), apc (absolute pitch class), dpc (diatonic pitch class)", \
                            type=str, choices=['ap','dp', 'apc','dpc'], default='dp')
        parser.add_argument("--format", "-f",help="Save output format. Default is json", type=str, choices=['csv','json','xlsx'], default='json' )
        parser.add_argument("--sort", help="Sort resulting MarkovChain ascending on both axes", action="store_true", default=False)
        #
        # Producer arguments
        #
        parser.add_argument("--chainFiles", "-c", help="Existing serialized MarkovChain and Durations files (--format type).",  type=str, default=None)
        
        parser.add_argument("--show", help="How to display resulting score", type=str, choices=['text','musicxml','midi'], default='musicxml')
        parser.add_argument("--name", help="Base name of generated files", type=str, default="MyScore")
        parser.add_argument("--title", help="Title of the generated Score", type=str, default="MyScore")
        parser.add_argument("--measures", "-m",  help="Total number of measures per part to produce",  type=int, default=10)
        parser.add_argument("--verbose", "-v", help="increase output verbosity", action="count", default=0)
        
        parser.add_argument("--produce", help="Comma-delimited list of Part name(s) to produce. A part name must also be a valid instrument name", \
                            type=str, action="extend", nargs="+", choices=Instruments.instrument_names,  default=None)
        parser.add_argument("--notes", help="For Interval chains, the starting note for each Part", type=str, default=None)   
        parser.add_argument("--enforceRange", "-e", help="Enforce ranges of selected instruments", action="store_true", default=False)
        parser.add_argument("--key", "-k", \
                            help="Key to use for all parts. Specify a single pitch. Lower case is minor, upper case is major. Key is adjusted for transposing instruments.", default=None)
        
        parser.add_argument("--seedNotes", help="Initial seed, number of args must be equal to the order of source chain", type=str, nargs='*', default=None)
        parser.add_argument("--seedIntervals", help="Initial seed, number of args must be equal to the order of source chain", type=int, nargs='*', default=None)
        parser.add_argument("--initial", help="choose initial seed only", action="store_true", default=False)
        parser.add_argument("--recycle", help="How often to pick a new seed in terms of number of notes/intervals.", type=int, default=5)
        parser.add_argument("--trace", help="Show notes/intervals as they are produced", action="store_true", default=False)
        parser.add_argument("--duration","-d", help="Specify fixed duration as a quarterLength.", type=float, default=None)
        args = parser.parse_args()
        markovChain = None
        if args.verbose > 0:
            print('run ScoreProducer')
            print(args)
        randomseed = Utils.time_since()
        durationsChain = None
        markovChain = None
        collector = None
        if args.chainFiles is None and args.source is not None:
            #
            # run the appropriate collector first to produce the MarkovChains
            #
            if args.type== 'notes':
                collector = NoteCollector(state_size = args.order, verbose=args.verbose, source=args.source, parts=args.parts, collection_mode=args.mode )
            elif args.type == 'intervals':
                collector = IntervalCollector(state_size = args.order, verbose=args.verbose, source=args.source, parts=args.parts )
            
            collector.name = args.name
            collector.format = args.format
            collector.sort_chain = args.sort
            run_results = collector.run()
            if run_results['save_result']:
                print(f"MarkovChain written to file: {collector.filename}")
            markovChain = collector.markovChain
            durationsChain = collector.durationCollector.markovChain
        else:
            env = Environment.get_environment()
            save_folder = env.get_resource_folder('music')
            
            # use serialized MarkovChain in specified format, and Durations files in csv format as input
            file_list = []
            order = f'0{args.order}'
            file_list.append('{}/{}_{}Counts_{}.{}'.format(save_folder, args.chainFiles, 'durations', order, args.format))
            file_list.append('{}/{}_{}Chain_{}.{}'.format(save_folder, args.chainFiles, 'durations', order, args.format))
            if args.type == 'notes':
                file_list.append('{}/{}_{}Counts_{}_{}.{}'.format(save_folder, args.chainFiles, args.type, args.mode, order, args.format))
                file_list.append('{}/{}_{}Chain_{}_{}.{}'.format(save_folder, args.chainFiles, args.type, args.mode, order, args.format))
            else:   # there is no mode for intervals, as in 'bwv37x_intervalsChain_02.csv'
                file_list.append('{}/{}_{}Counts_{}.{}'.format(save_folder, args.chainFiles, args.type, order, args.format))
                file_list.append('{}/{}_{}Chain_{}.{}'.format(save_folder, args.chainFiles, args.type, order, args.format))                
            
            i = 0
            counts_df = None
            durations_counts_df = None
            for chainFile in file_list:
                file_info = Utils.get_file_info(chainFile)
                thepath = file_info["path_text"]
                ext = file_info['extension'].lower()
                if args.verbose > 0:
                    print(file_info)
                if not file_info['Path'].exists():
                    print(f"{thepath} does not exist")
                    exit()
                else:
                    if ext == 'json':
                        mc_df = pd.read_json(thepath, orient="index")
                    elif ext == 'csv':
                        mc_df = pd.read_csv(thepath)
                        # need to reindex and then drop the KEY column
                        new_index = mc_df['KEY']
                        mc_df.index = new_index.values
                        mc_df.drop(['KEY'],axis=1,inplace=True)
                    if i==0:    # notes/intervals counts file
                        counts_df = mc_df
                        i=1
                        continue
                    elif i==1:  # durations counts file
                        durations_counts_df = mc_df
                        i=2
                        continue
                    elif i==2:
                        markovChain = MarkovChain(args.order, counts_df, chain_df=mc_df)
                        i=3
                    elif i==3:
                        durationsChain = MarkovChain(args.order, durations_counts_df, chain_df=mc_df)
                        i=0

        
        musicProducer = MusicProducer(
            args.order, markovChain, durationsChain, \
            args.source, args.parts, args.produce, \
            num=args.measures, verbose=args.verbose, \
            rand_seed=randomseed, producerType=args.type )
        
        musicProducer.show = args.show
        musicProducer.name = args.name
        musicProducer.recycle_seed_count = args.recycle
        musicProducer.initial = args.initial
        musicProducer.enforceRange = args.enforceRange
        musicProducer.trace_mode = args.trace
        musicProducer.fixed_duration = args.duration
        musicProducer.collection_mode = args.mode
        if args.key is not None:
            musicProducer.score_key = key.Key(args.key)
        #
        # order 2 examples:
        #  --seedIntervals -1 -2   for intervals
        #  --seedNotes C4 D4   for notes (dp, ap) --seed C D   for notes (dpc, apc)
        if args.seedIntervals is not None:
            musicProducer.set_seed(args.seedIntervals, args.type)
        if args.seedNotes is not None:
            musicProducer.set_seed(args.seedNotes, args.type)
        
        #
        # intervals producerType needs starting note(s) for each Part
        #
        if args.type == 'intervals':
            musicProducer.add_part_notes(args.notes)
                
        theScore = musicProducer.produce()
        if theScore is not None:
            theScore.metadata.title = args.title
            theScore.show(args.show)
        print("Done")
