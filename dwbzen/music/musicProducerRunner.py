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
import pandas as pd

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
        parser.add_argument("order", help="the order of the Markov Chain", type=int, choices=range(1,5))
        parser.add_argument("-s", "--source", help="input file (.mxl or .musicxml), folder name, or composer name ('bach' for example)", default=None)
        parser.add_argument("-t", "--type", help="Source object type: note or interval", type=str, choices=['notes','intervals'], default='intervals')
        parser.add_argument("-p","--parts", help="part name(s) or number(s) to include in building the MarkovChain", type=str, default=None)
        parser.add_argument("-f","--format", help="Save output format. Default is json", type=str, choices=['csv','json','xlsx'], default='json' )
        parser.add_argument("--sort", help="Sort resulting MarkovChain ascending on both axes", action="store_true", default=False)
        #
        # Producer arguments
        #
        parser.add_argument("-c", "--chainFiles", help="Existing serialized MarkovChain and Durations files (json).",  type=str, default=None)
        
        parser.add_argument("--show", help="How to display resulting score", type=str, choices=['text','musicxml','midi'], default='musicxml')
        parser.add_argument("--name", help="Name of resulting score, used to save to .musicxml file", type=str, default=None)
        parser.add_argument("-n", "--num", help="Total number of measures per part to produce",  type=int, default=10)
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        
        parser.add_argument("--produce", help="Comma-delimited list of Part name(s) to produce. A part name must also be a valid instrument name", \
                            type=str, action="extend", nargs="+", choices=music.Instruments.instrument_names,  default=None)
        parser.add_argument("--notes", help="For Interval chains, the starting note for each Part", type=str, default=None)
        
        # parser.add_argument("--clefs", help="Clef to use for each Part.", type=str, action="extend", nargs="+", choices=music.Instruments.clef_names,  default=None)
        # parser.add_argument("--instruments", help="Instrument to assign to each Part", type=str, action="extend", nargs="+", choices=music.Instruments.instrument_names,  default=None)
        
        parser.add_argument("--enforceRange", "-e", help="Enforce ranges of selected instruments", action="store_true", default=False)
         
        parser.add_argument("--seed", help="Initial seed, length must be equal to the order of source chain", type=str, default=None)
        parser.add_argument("--initial", help="choose initial seed only", action="store_true", default=False)
        parser.add_argument("--recycle", help="How often to pick a new seed in terms of number of notes.", type=int, default=5)
        args = parser.parse_args()
        markovChain = None
        if args.verbose > 0:
            print('run ScoreProducer')
            print(args)
        randomseed = music.Utils.get_timedelta()
        durationsChain = None
        markovChain = None
        collector = None
        if args.chainFiles is None and args.source is not None:
            #
            # run the collector first to produce the MarkovChain
            #
            if args.type.startswith('note'):
                collector = music.NoteCollector(state_size = args.order, verbose=args.verbose, source=args.source, parts=args.parts )
            elif args.type.startswith('interval'):
                collector = music.IntervalCollector(state_size = args.order, verbose=args.verbose, source=args.source, parts=args.parts )
            
            collector.name = args.name
            collector.format = args.format
            collector.sort_chain = args.sort
            run_results = collector.run()
            if run_results['save_result']:
                print(f"MarkovChain written to file: {collector.filename}")
            markovChain = collector.markovChain
            durationsChain = collector.durationCollector.markovChain
        else:
            # use serialized MarkovChain and Durations files in JSON format as input
            file_list = []
            file_list.append('{}/{}_{}.json'.format(music.MusicCollector.save_folder, args.chainFiles, args.type))
            file_list.append('{}/{}_{}.json'.format(music.MusicCollector.save_folder, args.chainFiles, 'durations'))

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
                    mc_df = pd.read_json(thepath, orient="index")
                    if i==0:
                        markovChain = common.MarkovChain(args.order, chain_df=mc_df)
                        i=i+1
                    else:
                        durationsChain = common.MarkovChain(args.order, chain_df=mc_df)
        
        musicProducer = music.MusicProducer(args.order, markovChain, durationsChain, args.source, args.parts, args.produce, num=args.num, verbose=args.verbose, rand_seed=randomseed, producerType=args.type)
        musicProducer.show = args.show
        musicProducer.name = args.name
        musicProducer.recycle_seed_count = args.recycle
        musicProducer.initial = args.initial
        musicProducer.enforceRange = args.enforceRange
        #
        # order 2 examples:
        #  --seed "-1, -2"  for intervals
        #  --seed "-C4, D4" for notes 
        if args.seed is not None:
            musicProducer.set_seed(args.seed)
        
        #
        # intervals producerType need a starting note for each Part
        #
        if args.type == 'intervals':
            musicProducer.add_part_notes(args.notes)
        
        #
        # instrument clefs automatically assigned by Instrument class
        #
        #if args.clefs is None:
        #    clefs = ['Treble']
        #else:
        #    clefs = args.clefs
        #musicProducer.add_part_clefs(clefs)
        
        #
        # assign an Instrument to each Part.
        # If unspecified use produceParts as the instrument names
        #
        #if args.instruments is None:
        #    instrument_names = ['Piano']
        #else:
        #    instrument_names = args.instruments
        #musicProducer.add_part_instruments(instrument_names)

        
        theScore = musicProducer.produce()
        if theScore is not None:
            theScore.show(args.show)
            
