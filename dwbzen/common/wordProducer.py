# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       WordProducer class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from .producer import Producer
import random


class WordProducer(Producer):
    
    def __init__(self, state_size, markovChain, source_file, min_size=0, max_size=0, num=10, verbose=0, rand_seed=42):
        super().__init__(state_size, markovChain, source_file, min_size, max_size, num, verbose, rand_seed)
        self.list=False
        self.postprocessing = None
        self.initial=False
        self.pos=False

        self.initial_keys = self.keys[self.keys.apply(lambda s:s.startswith(' '))]

        self.terminal_character = '~'   # needs to match the CharacterCollector terminal_character
        self.output_format = 'TC'   # title case, can also do UC = upper case, LC = lower case
    
    def __str__(self):
        return f"WordProducer order={self.order} verbose={self.verbose}, source={self.source}, min/max={self.min_size},{self.max_size} seed={self.seed}, num={self.num}"
    
    def get_seed(self, aseed=None):
        if self.seed is None or aseed is None or len(self.seed)!=self.order:
            # need to pick one at random
            if self.initial:
                # pick a seed that starts a word (i.e. first character is a blank)
                theseed = self.initial_keys[random.randint(0, len(self.initial_keys)-1)]
            else:
                # pick any old seed from the chain's index
                theseed = self.keys[random.randint(0, len(self.keys)-1)]
        else:
            theseed = aseed
        return theseed
    
    def get_next_seed(self):
        """
        checks the seed_count against the recycle_seed_count
        and if >= gets a new seed, otherwise returns the existing one
        """
        self.seed_count = self.seed_count + 1
        aseed = self.seed
        if self.seed_count >= self.recycle_seed_count:
            # pick a new seed
            aseed = self.get_seed()
            self.seed_count = 0
        return aseed
    
    def get_next_character(self, seed):
        """Gets the next character based on the seed argument
        
        Returns:
            both the next character and a new seed as a dict with keys 'new_seed' and 'next_token'
        """
        
        new_seed = None
        next_token = None
        if self.verbose > 2:
            print(f"get_next_character(seed): '{seed}'")
        key_values = self.keys.values
        if seed in key_values:
            row = self.chain_df.loc[seed]
            row_probs = row[row > 0].cumsum()
            # given a probability, pick the first character in the row_probs (cumulative probabilities)
            # having a probability > the random probability
            # for example:
            prob = random.random()
            p = row_probs[row_probs> prob].iat[0]
            next_token = row_probs[row_probs> prob].index[0]
            new_seed = (seed + next_token)[1:self.order+1]
            if self.verbose > 1:
                print(f"random prob: {prob}, row prob: {p}, seed: '{seed}', next_token: '{next_token}', new_seed: '{new_seed}'")
        return dict([ ('next_token', next_token), ('new_seed',new_seed)])
    
    def add_word_to_list(self, word_list, aword):
        if self.output_format == 'TC':
            aword = aword.title()
        elif self.output_format == 'LC':
            aword = aword.lower()
        elif self.output_format == 'UC':
            aword = aword.upper()
        else:
            pass
        word_list.append(aword)
        return aword

    def produce(self):
        """
        Produce a list of words using the MarkovChain probabilities
        """
        words = []
        initial_seed = self.get_seed(self.seed)      # get the initial seed
        seed = initial_seed
        if self.verbose > 0:
            print(f"initial seed: '{seed}'")
        if self.verbose > 1:
            print(f" MarkovChain:\n {self.markovChain}")
        for n in range(1, self.num+1):
            word = seed.strip()
            more_to_go = True
            if self.verbose > 1:
                print(f"generating word {n}")
            while more_to_go:
                nc_dict = self.get_next_character(seed)
                ntoken = nc_dict['next_token']
                nseed = nc_dict['new_seed']
                if ntoken is not None:
                    if ntoken==self.terminal_character:     # done with this word
                        if len(word) < self.min_size:
                            pass
                        else:
                            word = self.add_word_to_list(words, word)
                            more_to_go = False
                            seed = self.get_next_seed()
                    else:
                        word = word + ntoken
                        if len(word) >= self.max_size:
                            word = self.add_word_to_list(words, word)
                            more_to_go = False
                            seed = self.get_next_seed()
                        else:
                            more_to_go = True
                            seed = nseed
                else:
                    # there is no next token for the current seed, so done with this word
                    word = self.add_word_to_list(words, word)
                    more_to_go = False
                    seed = initial_seed             # start next word with the initial_seed selected earlier
                    
            print(f"{word}")
        if self.sort:
            words = words.sort(key=str.lower, reverse=False)
        return words

    if __name__ == '__main__':
        print(WordProducer.__doc__)

