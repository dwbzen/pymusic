# ------------------------------------------------------------------------------
# Name:          sentenceProducer.py
# Purpose:       SentenceProducer class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright 2022 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from common.producer import Producer
from common.textParser import TextParser
import random

class SentenceProducer(Producer):
    
    def __init__(self, state_size, markovChain, source_file, min_size=0, max_size=0, num=10, verbose=0, rand_seed=42):
        super().__init__(state_size, markovChain, source_file, min_size, max_size, num, verbose, rand_seed)
        self.list=False
        self.postprocessing = None
        self.initial=False
        self.pos=False

        self.terminal_characters = '.?!'   # needs to match the WordCollector terminal_characters
        self.output_format = 'TC'          # title case, can also do UC = upper case, LC = lower case

        self._set_keys()
    
    def __str__(self):
        return f"SentenceProducer order={self.order} verbose={self.verbose}, source={self.source}, min/max={self.min_size},{self.max_size} seed={self.seed}, num={self.num}"

    def _set_keys(self):
        prefix = TextParser._prefix
        self._initial_keys_df = self.counts_df[ [x.startswith(prefix) for x in self.counts_df['key']] ]
        #
        # initiial_keys and keys are both sets and so the values are unique
        #
        self._initial_keys = list(set(self._initial_keys_df['key'].values.tolist()))
        self._keys = list(set(self.counts_df['key'].values.tolist()))
        if self.verbose > 0:
            print(f'total number of keys: {len(self._keys)}')
            print(f'number of initial keys: {len(self._initial_keys)}')

    def get_seed(self, aseed=None):
        if self.seed is None or aseed is None:
            # need to pick one at random
            if self.initial:
                # pick a seed that starts a sentence (i.e. first character is a space)
                theseed = self._initial_keys[random.randint(0, len(self._initial_keys)-1)]
            else:
                # pick any old seed from the chain's index
                theseed = self._keys[random.randint(0, len(self._keys)-1)]
        else:
            theseed = aseed
        if self.verbose > 1:
            print(f'get seed: {theseed}')
        return theseed
    
    def get_next_word(self, seed):
        """Gets the next word based on the seed argument

        Returns:
            both the next word and a new seed as a dict with keys 'new_seed' and 'next_token'
        """
        
        new_seed = None
        next_token = None
        if self.verbose > 2:
            print(f"get_next_word(seed): '{seed}'")

        if seed in self._keys:
            df = self.chain_df[self.chain_df['key']==seed]
            if len(df) == 0:  #  add to chain_df from counts_df
                df = self._add_key(seed)
    
            # given a probability, pick the first word in the row_probs (cumulative probabilities)
            # having a probability > the random probability
            # for example:
            prob = random.random()
            row = df[df['prob']>prob].iloc[0]
            next_token = row['word'].lstrip()
            p = row['prob']
            
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
        if self.display_as_produced:
            print(asentence)
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
                        sentence = f'{sentence} {ntoken.lstrip()}'
                        nwords+=1
                        if nwords >= self.max_size:
                            sentence = self.add_sentence_to_set(sentences, sentence + '.')
                            more_to_go = False
                            seed = self.get_next_seed()    # pick a new seed
                            nwords = self.order
                        else:
                            more_to_go = True
                            seed = nseed
                else:  
                    # this can happen when the collector is in processing sentences mode
                    # add the sentence as is and get a new seed
                    sentence = self.add_sentence_to_set(sentences, sentence + '.')
                    seed = self.get_seed()
                    nwords = self.order
                    more_to_go = False
                
        return sentences

if __name__ == '__main__':
    print(SentenceProducer.__doc__)
