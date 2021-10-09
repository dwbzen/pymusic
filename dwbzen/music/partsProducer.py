# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       PartsProducer class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import common
import pandas as pd
import pathlib
import numpy as np
import random

class PartsProducer(common.Producer):
    
    def __init__(self, state_size, markovChain, source_file, min_size=0, max_size=0, num=10, verbose=0, rand_seed=42):
        super().__init__(state_size, markovChain, source_file, min_size, max_size, num, verbose, rand_seed)
        
    def __str__(self):
         return f"PartsProducer order={self.order} verbose={self.verbose}, source={self.source}, min/max={self.min_size},{self.max_size} seed={self.seed}, num={self.num}"
       
