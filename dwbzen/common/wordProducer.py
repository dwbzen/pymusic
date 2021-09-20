# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       Base Producer class.
#
#
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import common
import pandas as pd
import argparse

class WordProducer(common.Producer):
    
    def __init__(self, chain, min_size=0, max_size=0, trace = False):
        super().__init__(chain, min_size, max_size, trace)
    
    if __name__ == '__main__':
        print('run WordProducer')
