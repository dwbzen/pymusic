
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:          noteCollector.py
# Purpose:       Note collector class.
#
#                NoteCollector creates a pair of MarkovChains
#                from a Note stream (strings) for the pitches and durations.
#                The corresponding Producer class is PartProducer which reverses the process.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright � 2021 Donald Bacon

# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import common
from music21 import stream, interval, note

class NoteCollector(common.Collector):

    def __init__(self, state_size):
        super().__init__(state_size)

    def __repr__(self):
        return f"NoteCollector {self.order}"

    def get_base_type(self):
        return note.Note
