# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:          intervalCollector.py
# Purpose:       Note collector class.
#
#                IntervalCollector creates a pair of MarkovChains
#                from a Note stream for the Intervals and Durations. 
#                The corresponding Producer class is PartProducer which reverses the process.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import common
from music21 import stream, interval,duration, corpus

class DurationCollector(common.Collector):

    def __init__(self, state_size):
        super().__init__(state_size)

    def __repr__(self):
        return f"DurationCollector {self.order}"

    def get_base_type(self):
        return duration.Duration
    