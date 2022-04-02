
from common import RuleSet, SubstitutionSystem
import music
import argparse

class MusicSubstitutionSystem(SubstitutionSystem):
    '''Generates a list representing the evolution of the substitution system with the specified rule 
        from initial condition init for t steps.
        Arguments:
            substitution_rules - 
            start - initial condition
            t - the number of steps (generations) as a range(n1, n2)
                where n1 is the starting step, and n2-1 is the ending step, 0 <= n1 <= n2
                For example, t=range(1, 4) will output the results of steps 1,2 and 3
                t=range(2, 3) step 2 only.
                t=range(2, 4) steps 2 and 3
    '''
    
    def __init__(self, rule_set:RuleSet, verbose=0):
        super().__init__(rule_set, tags=['interval', 'duration'], verbose=verbose)

    
    def apply(self, start:[str], nsteps):
        '''Apply the substitution to the start string for a given number of steps.
         The result is a command list that can be input to a music generation module.
        '''
        sub_result = start
        self.steps = nsteps
        if nsteps > 0:
            sub_result = start
            for step in range(nsteps):
                sub_result = self.apply_step(sub_result)
                if self.verbose > 1:
                    print(f'step: {step}\nresult: {sub_result}')
        return sub_result
            
        
    def apply_step(self, start:[str]):
        subst_result = []
        for subs in self.substitutions:
            pattern = subs["pattern"]
            replacement = subs["replacement"]

            # try to match each item in start (result) list
            # 
            for s in start:
                if self.verbose > 1:
                    print(f's: "{s}"    pattern: {pattern.pattern}')
                match = pattern.match(s)
                if match is not None:
                    if self.verbose > 0:
                        print(f'"{s}" matched pattern {pattern.pattern} ')
                    grp_dict = match.groupdict()
                    #
                    # now substitute
                    #
                    subst_result += replacement
                else:
                    subst_result += [s]
            if self.verbose > 0:
                print(f'step result: {subst_result} \n')
        return subst_result
    
    if __name__ == '__main__':
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--steps", "-s", help="number of steps to run", type=int, choices=range(1,10), default=1)
        parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
        args = parser.parse_args()
        
        substitution_rules = {\
            r'(?P<interval>[+-]?0)/(?P<duration>\d+\.\d+)':['0/0.5', '+1/1.0', '-2/1.0', '+1/2.0'], \
            r'(?P<interval>[+-]?1)/(?P<duration>\d+\.\d+)' : ['0/1.0', '1/0.5', '2/1.0']        }
        command_rules = {'interval' : music.MusicSubstitutionRules.interval_rule, 'duration' : music.MusicSubstitutionRules.duration_rule}
        rules = {'commands':command_rules}
        splitter = r'(?P<interval>[+-]?\d+)/(?P<duration>\d+\.\d+)'
        rule_set = RuleSet(substitution_rules, rules=rules, splitter=splitter)
        start = ['0/1.0', '+1/0.5']
        
        ss = music.MusicSubstitutionSystem(rule_set, verbose=args.verbose)
        commands = ss.apply(start,args.steps)
        print(f'{len(commands)} commands:\n{commands} ')
    
    
