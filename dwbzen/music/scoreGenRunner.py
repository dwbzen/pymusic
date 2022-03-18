
from common import RuleSet
import music
from music21 import key, note
import argparse

class ScoreGenRunner(object):
    '''Runs MusicSustitutionSystem and passes the result to ScoreGen
        For now, the RuleSet is hard-coded. TODO - make json

    '''
    if __name__ == '__main__':
        start = ['0/1.0', '+1/0.5', '-2/1.0', '1/2.0']
        parser = argparse.ArgumentParser()
        parser.add_argument("--scale", "-s", help="Scale name", type=str, default='Major')
        parser.add_argument("--part", "-p", help='Part name', type=str, default='Soprano')
        parser.add_argument("--key", "-k", help="Key, default is C-major", type=str, default='C')
        parser.add_argument("--steps", "-n", help="number of steps to run", type=int, choices=range(0,10), default=1)
        parser.add_argument("--start", help="starting commands", type=str, nargs='*', default=start)
        parser.add_argument("--note", help="Starting note with octave", type=str, default="C5")
        parser.add_argument("--duration", "-d", help="Starting note duration in quarterLengths", type=float, default=4.0)
        parser.add_argument("--show", help="How to view the resulting score, default is musicxml", type=str, default='musicxml')
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        parser.add_argument("--trace", "-t", help="Trace rule processing", action="store_true", default=False)
        args = parser.parse_args()
        
        #
        # hard-coded rule set
        #
        substitution_rules = {\
            r'(?P<interval>[+-]?[01])/(?P<duration>\d+\.\d+)':['0/0.5', '+3/1.0', '-2/2.0', '-1/0.5']  , \
            r'(?P<interval>[+-]?[234])/(?P<duration>\d+\.\d+)' : ['-1/1.0', '-2/2.0']
        }
        command_rules = {'interval' : music.MusicSubstitutionRules.interval_rule, 'duration' : music.MusicSubstitutionRules.duration_rule}
        rules = {'commands':command_rules}
        splitter = r'(?P<interval>[+-]?\d+)/(?P<duration>\d+\.\d+)'
        rule_set = RuleSet(substitution_rules, rules=rules, splitter=splitter)
        
        music.MusicSubstitutionRules.trace = args.trace
        ss = music.MusicSubstitutionSystem(rule_set, verbose=args.verbose)
        commands = ss.apply(start,args.steps)
        print(f'{len(commands)} commands:\n{commands} \n')
        
        score_gen = music.ScoreGen(rule_set, scale_name=args.scale, instrument_name=args.part, key=key.Key(args.key), verbose=args.verbose)
        start_note=note.Note(args.note, quarterLength=args.duration)
        ascore = score_gen.run(commands, start_note=start_note)
        ascore.show(args.show)
        
        