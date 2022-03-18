from common import RuleSet

class SubstitutionSystem(object):
    '''Base substitution system class
    '''
    def __init__(self, rule_set:RuleSet, tags:[str]=None, verbose=0):
        '''Initialize code
            Arguments:
                rule_set - a RuleSet instance
                tags - a list of tags that can appear in substitution rules, default is None
        '''
        self.rule_set = rule_set
        self.substitutions = rule_set.substitutions
        self.tags = tags
        self.verbose = verbose
