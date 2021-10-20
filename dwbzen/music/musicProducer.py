# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       PartsProducer class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import music, common
import pandas as pd
import random

class MusicProducer(common.Producer):
    
    def __init__(self, state_size, markovChain, source_file, parts, produceParts, num, verbose=0, rand_seed=42, producerType=None):
        super().__init__(state_size, markovChain, source_file, num=num, verbose=verbose,  rand_seed=rand_seed)
        self.show = None
        self.producerType = producerType
        self.save_folder="/Compile/dwbzen/resources/music"
        self.score = None
        self.parts = parts                  # comma-delimited filter part names from the command line
        self.produceParts = produceParts    # comma-delimited production part names from the command line
        self.part_names, self.part_numbers = MusicProducer.add_parts(parts)
        self.producePart_names, self.producePart_numbers = MusicProducer.add_parts(produceParts)
        self.durations_chain = None
    
    @classmethod
    def add_parts(self, parts:str) -> []:
        part_names = []
        part_numbers = []
        if parts is not None:
            parts_list = parts.split(",")   # could be numbers or names
            for p in parts_list:
                if p.isdigit():   # all digits
                    part_numbers.append(int(p))
                else:
                    part_names.append(p)
            return (part_names, part_numbers)

    def __str__(self):
        return f"MusicProducer order={self.order}, source={self.source_file}, num={self.num}, producerType={self.producerType}, \
parts={self.parts}, produce={self.produceParts}, verbose={self.verbose}"
       
    def produce(self):
        """Produce a Score from a MarkovChain

        """
        print(self.__str__())
        
        return self.score
    
    
    if __name__ == '__main__':
        print(MusicProducer.__doc__)
        
        