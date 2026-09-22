# ------------------------------------------------------------------------------
# Name:          scales.py
# Purpose:       Encapsulate music scales.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2026 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

from music.chordLibrary import ChordLibrary
from music.chord import Chord
from music.keys import Keys
from music.key import  Key
import argparse
import sys
from typing import List
import music21


class Chords(object):
    """ Utility to display chords in a specific format. """

    def __init__(self, key:Key, chords_filename:str=None):
        """ Constructor """
        self.chordLibrary = ChordLibrary(chords_filename)
        self.key_name = key.key_name
        self.key = key
        self.chords_data = self.chordLibrary.chordsData     # List[dict] from the chords JSON file
    
    def getChord(self, name:str, fmt, rootNote:str="C")->Chord:
        chord = self.chordLibrary.getChord(name, fmt, rootNote, self.key)
        return chord
        

def main():
    keys = Keys()
    key_names = keys.key_names
    description = "Display a chord from a Chordlibrary of Chords created from a JSON chords file. Show a named chord in a specified format."
    parser = argparse.ArgumentParser(prog="Chords", description=description)
    parser.add_argument("--name", "-N", help="Chord name", type=str, default=None)
    parser.add_argument("--group","-G",  help="Group name", type=str, default=None)
    parser.add_argument( "--root", "-R",help="Root pitch, default is 'C'. May also include an octave as in 'D3'", type=str, default="C")
    parser.add_argument("--key", "-K", 
        help="Optional key signature, for example 'Eb-Major', default key signature is 'C-Major'. Used to determine accidentals in the chords and the chord root note.",
        choices = key_names, type=str, default="C-Major")
    parser.add_argument("--dup", help="Duplicate the chord in a separate part, the number of octaves higher or lower as indicated",
        type=int, choices=list(range(-1, 1)), default=0 )
    parser.add_argument("--show", "-S", help="Display a chord in MuseScore, lilypond or as a list of notes/pitches",  
        type=str, choices=["pitches", "notes", "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf"], default="text")
    parser.add_argument("--duration", help="Duration of the notes. Default is 'quarter'", type=str, 
        choices=["whole","half","quarter","eighth","16th"], default="whole")
    parser.add_argument("--instrument", help="The instrument name, default is 'Piano'", type=str, default="Piano")
    parser.add_argument("--fmt", help="How to display the notes: in a condensed format (within a single octave), or extended.",
        type=str, choices=["condensed", "extended"], default="extended")
    args = parser.parse_args()
    
    key:Key = keys.key(args.key)
    chords = Chords(key)
    if args.name is not None:
        chord = chords.getChord(args.name, args.fmt, rootNote=args.root)
        if chord is None:
            print(f"The chord '{args.name}' not found", file=sys.stderr)
            sys.exit()
            
        chord.show(args.show, root=args.root, note_duration=args.duration, instrument_name=args.instrument, 
                   second_part_transpose=args.dup, metronome_mark=(100,"quarter"))
    

if __name__ == '__main__':
    main()
    