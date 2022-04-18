
from common.ruleSet import RuleSet
from music.scoreGen import ScoreGen
from music.musicSubstitutionRules import MusicSubstitutionRules
from music.musicSubstitutionSystem import MusicSubstitutionSystem
from music.musicUtils import MusicUtils
from music21 import key, note
import argparse, json
import environment

class ScoreGenRunner(object):
    '''Runs MusicSustitutionSystem and passes the result to ScoreGen
        For now, the RuleSet is hard-coded. TODO - make json

    '''
    if __name__ == '__main__':
        
        env = environment.Environment.get_environment()
        resource_folder = env.get_resource_folder('music')
        start = ['0/1.0', '+1/0.5', '-2/1.0', '1/2.0']
        parser = argparse.ArgumentParser()
        parser.add_argument("--scale", "-s", help="Scale name", type=str, default='Major')
        parser.add_argument("--parts", "-p", help='Part name(s)', type=str,  nargs='*', default=['Soprano'])
        parser.add_argument("--key", "-k", help="Key, default is C-major", type=str, default='C')
        parser.add_argument("--steps", "-n", help="number of steps to run", type=int, choices=range(0,10), default=1)
        parser.add_argument("--start", help="starting commands", type=str, nargs='*', default=start)
        parser.add_argument("--notes", help="Starting note(s) with octave", type=str, nargs='*', default=["C5"])
        parser.add_argument("--duration", "-d", help="Starting note duration in quarterLengths", type=float, default=4.0)
        parser.add_argument("--show", help="How to view the resulting score, default is musicxml", type=str, default='musicxml')
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        parser.add_argument("--trace", "-t", help="Trace rule processing", action="store_true", default=False)
        #
        # specifies substitution rules JSON file and the substitution rule name
        # default file is 'resources/music/substitution_rules.json'
        # Need to specify a rule name for each part OR the hard-coded substitution_rules is used for all parts
        #
        parser.add_argument("--rules", "-r", help="Substitution rules JSON file name", type=str, default=f'{resource_folder}/substitution_rules.json')
        parser.add_argument("--rulenames", help="Rule name(s) in Substitution rules JSON file.", type=str, nargs='*', default=None)
        args = parser.parse_args()
        
        #
        # default hard-coded rule set to use if Substitution rules name is not specified
        #
        substitution_rules = {\
            r'(?P<interval>[+-]?[01])/(?P<duration>\d+\.\d+)':['0/0.5', '+3/1.0', '-2/2.0', '-1/2.0']  , \
            r'(?P<interval>[+-]?[23])/(?P<duration>\d+\.\d+)' : ['-1/1.0', '-2/2.0', '+2/0.5', '0/1.0']
        }

        #
        # generate for each part
        #
        ascore = None
        for partnum in range(len(args.parts)):
            partname = args.parts[partnum]
            if args.rulenames is not None:
                fp = open(args.rules, "r")
                jtxt = fp.read()
                jdoc = json.loads(jtxt)
                substitution_rules = jdoc[args.rulenames[partnum]]
                
            command_rules = {'interval' : MusicSubstitutionRules.interval_rule, 'duration' : MusicSubstitutionRules.duration_rule}
            rules = {'commands':command_rules}
            splitter = r'(?P<interval>[+-]?\d+)/(?P<duration>\d+\.\d+)'
            rule_set = RuleSet(substitution_rules, rules=rules, splitter=splitter)
            
            MusicSubstitutionRules.trace = args.trace
            MusicUtils.verbose = args.verbose
            ss = MusicSubstitutionSystem(rule_set, verbose=args.verbose)
            commands = ss.apply(start,args.steps)
            print(f'{len(commands)} commands:\n{commands} \n')
            
            score_gen = ScoreGen(rule_set, scale_name=args.scale, instrument_name=partname, key=key.Key(args.key), verbose=args.verbose)
            start_note=note.Note(args.notes[partnum], quarterLength=args.duration)
            score_gen.run(commands, start_note=start_note)
            if ascore is None:
                maxpartlen = score_gen.part.duration
                ascore = score_gen.score
            else:
                if maxpartlen.quarterLength < score_gen.part.duration.quarterLength:
                    maxpartlen = score_gen.part.duration
                ascore.append(score_gen.part)
                
        MusicUtils.extend_parts(ascore, maxpartlen)
        ascore.show(args.show)
        
        