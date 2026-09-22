'''
Created on Sep 21, 2026

@author: dwbze
'''
import unittest
from music.keys import Keys
from music.key import  Key
from music.chord import Chord
from music.chords import Chords

class ChordTest(unittest.TestCase):
    
    keys = Keys()
    key_name = "C-Major"
    key = keys.key(key_name)
    chords = Chords(key)

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def testgetChord_1(self):
        chord_name = "Major seventh"
        rootNote:str="C"
        print(f"\n****** test create {chord_name} Chord, root: {rootNote}  ==========================")

        chords = Chords(ChordTest.key)
        fmt = "condensed"
        chord:Chord = chords.getChord(chord_name, fmt)
        if chord is None: 
            print(f"The chord '{chord_name}' not found")
        assert chord is not None

        chord.show(format_="musicxml", root="C4")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()