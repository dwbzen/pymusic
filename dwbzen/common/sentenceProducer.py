# ------------------------------------------------------------------------------
# Name:          sentenceProducer.py
# Purpose:       SentenceProducer class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright 2022 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from .producer import Producer
import random, sys

class SentenceProducer(Producer):
    
    def __init__(self, state_size, markovChain, source_file, min_size=0, max_size=0, num=10, verbose=0, rand_seed=42):
        super().__init__(state_size, markovChain, source_file, min_size, max_size, num, verbose, rand_seed)
        self.list=False
        self.postprocessing = None
        self.initial=False
        self.pos=False
        #
        # initial words start with a space character  keys = self.chain_df.index
        #
        self.initial_keys = self.keys[self.keys.apply(lambda s:s.startswith(' '))]

        self.terminal_characters = '.?!'   # needs to match the WordCollector terminal_characters
        self.output_format = 'TC'          # title case, can also do UC = upper case, LC = lower case
    
    def __str__(self):
        return f"SentenceProducer order={self.order} verbose={self.verbose}, source={self.source}, min/max={self.min_size},{self.max_size} seed={self.seed}, num={self.num}"

    def get_seed(self, aseed=None):
        if self.seed is None or aseed is None:
            # need to pick one at random
            if self.initial:
                # pick a seed that starts a sentence (i.e. first character is a space)
                theseed = self.initial_keys.iloc[random.randint(0, len(self.initial_keys)-1)]
            else:
                # pick any old seed from the chain's index
                theseed = self.keys.iloc[random.randint(0, len(self.keys)-1)]
        else:
            theseed = aseed
        if self.verbose > 1:
            print(f'get seed: {theseed}')
        return theseed
    
    def get_next_word(self, seed):
        """Gets the next word based on the seed argument
        
        The algorithm is identical to WordProducer.get_next_character
        Returns:
            both the next word and a new seed as a dict with keys 'new_seed' and 'next_token'
        """
        
        new_seed = None
        next_token = None
        if self.verbose > 2:
            print(f"get_next_word(seed): '{seed}'")
        key_values = self.keys.values
        if seed in key_values:
            row = self.chain_df.loc[seed]
            row_probs = row[row > 0].cumsum()
            # given a probability, pick the first word in the row_probs (cumulative probabilities)
            # having a probability > the random probability
            # for example:
            prob = random.random()
            p = row_probs[row_probs> prob].iat[0]
            next_token = row_probs[row_probs> prob].index[0]
            new_seed = ' '.join(((seed + ' ' + next_token).split())[1:self.order+1])
            if self.verbose > 1:
                print(f"random prob: {prob}, row prob: {p}, seed: '{seed}', next_token: '{next_token}', new_seed: '{new_seed}'")
                
        return dict([ ('next_token', next_token), ('new_seed',new_seed)])

    def add_sentence_to_set(self, sentence_set, asentence):
        if self.output_format == 'TC':
            #
            # capitalize the first letter of the sentence
            #
            asentence = asentence[0].upper() + asentence[1:]
        elif self.output_format == 'LC':
            asentence = asentence.lower()
        elif self.output_format == 'UC':
            asentence = asentence.upper()
        else:
            pass
        sentence_set.add(asentence)
        
        if self.verbose > 1:
            print(f'added: {asentence}')
        return asentence
            
    def produce(self):
        """Produce a list of words using the MarkovChain probabilities
        
        """
        sentences = set()
        initial_seed = self.get_seed(self.seed)      # get the initial seed
        seed = initial_seed
        self.seed = seed
        if self.verbose > 0:
            print(f"initial seed: '{seed}'")
            
        for n in range(1, self.num+1):
            sentence = seed.strip()
            more_to_go = True
            #
            # add words to the sentence until it reaches a maximum length
            # or the next word is a terminator
            #
            nwords = self.order      # number of words in this sentence so far
            while more_to_go:
                nc_dict = self.get_next_word(seed)
                ntoken = nc_dict['next_token']
                nseed = nc_dict['new_seed']
                if self.verbose > 2:
                    print(f'ntoken: "{ntoken}"')
                    
                if ntoken is not None:
                    if ntoken in self.terminal_characters:
                        sentence = self.add_sentence_to_set(sentences, sentence)
                        more_to_go = False
                        seed = self.get_next_seed()
                        nwords = self.order
                    else:
                        sentence = f'{sentence} {ntoken}'
                        nwords+=1
                        if nwords >= self.max_size:
                            sentence = self.add_sentence_to_set(sentences, sentence + '.')
                            more_to_go = False
                            seed = self.get_next_seed()    # pick a new seed
                            nwords = self.order
                        else:
                            more_to_go = True
                            seed = nseed
                else:   # this is a problem - there should always be a new seed
                    print("Warning - next token is None", file=sys.stderr)
                    break
                
        return sentences

if __name__ == '__main__':
    print(SentenceProducer.__doc__)
