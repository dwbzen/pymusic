import re

class RuleSet(object):

    def __init__(self, substitution_rules:dict, rules=None, splitter:str=None):
        '''
        Each substitution is a dict. The key is a regular expression string used to match an input string,
        for example: (interval)/(quarterLength-multiplier)
        The value is the replacement. The re groups are named and can be referenced in the replacement.
        splitter is a regular expression, analagous to a string splitter, that will split the
        substitution result into named components.
        
        Sample substitutions:
           sub1 = {r'(?P<interval>[+-]?0)/(?P<duration>\d+\.\d+)':['0/0.5', '+1/1.0', '-2/1.0', '+1/2.0']}
           sub2 = {r'(?P<interval>[+-]?1)/(?P<duration>\d+\.\d+)' : ['0/<duration>', '1/0.5']}
           splitter = r'(?P<interval>[+-]?\d+)/(?P<duration>\d+\.\d+)'
        '''
        self.rules = rules
        self.substitutions = []
        self.substitution_rules = substitution_rules

        #
        # compile the substitution rules regular expressions
        #
        for k in self.substitution_rules.keys():
            pattern = re.compile(k)
            replacement = self.substitution_rules[k]
            self.substitutions.append({'pattern':pattern, 'replacement':replacement})
        
        self.pre_processing = None
        self.post_processing = None
        self.command_rules = None
        if splitter is not None:
            self.splitter = re.compile(splitter)
        if rules is not None:
                if 'preProcessing' in rules:
                    self.pre_processing = rules['preProcessing'] 
                if 'postProcessing' in rules:
                    self.post_processing = rules['postProcessing']
                if 'commands' in rules:
                    self.command_rules = rules['commands']
    