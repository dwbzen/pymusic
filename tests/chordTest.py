'''
Created on Sep 21, 2026

@author: dwbze
'''
import unittest
from music.keys import Keys
from music.key import  Key
from music.chord import Chord
from music.chords import Chords
from music.musicUtils import MusicUtils
from music21 import chord

class ChordTest(unittest.TestCase):
    
    keys = Keys()
    key_name = "C-Major"
    key = keys.key(key_name)
    chords = Chords(key)
    show_format = "text"    # "musicxml"

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def testgetChord_condensed(self):
        chord_name = "Major seventh"
        rootNote:str="C"
        print(f"\n****** test create {chord_name} Chord condensed (default) format, root: {rootNote}  ==========================")

        chords = Chords(ChordTest.key)
        fmt = "condensed"
        chord:Chord = chords.getChord(chord_name, fmt)
        assert chord is not None, f"The chord '{chord_name}' not found"

        chord.show(format_=ChordTest.show_format, root="C4", note_duration="whole")

    def testgetChord_extended(self):
        chord_name = "Dominant ninth"
        rootNote:str="C"
        fmt = "extended"
        print(f"\n****** test create {chord_name}  extended format, root: {rootNote}  ==========================")

        chords = Chords(ChordTest.key)
        chord:Chord = chords.getChord(chord_name, fmt)
        assert chord is not None, f"The chord '{chord_name}' not found"

        chord.show(format_=ChordTest.show_format, root="C4", note_duration="whole")

    def test_chord_notes_from_formula_1(self):
        formula = [4,3,3,4]
        print(f"\n****** test get chord notes from formula 1: {formula}  ==========================")
        rootPitch = "C4"
        chordNotes = Chord.chord_notes_from_formula(rootPitch, formula, inversion=0)
        s = [f"{n.nameWithOctave} " for n in chordNotes]
        print(f"chord notes: {s}")
        c:chord.Chord = chord.Chord(chordNotes)
        c.show(ChordTest.show_format,  root="C4", note_duration="whole")
        
    def test_chord_notes_from_formula_2(self):
        formula = [10,6,3,7]
        print(f"\n****** test get chord notes from formula 2: {formula}  ==========================")
        rootPitch = "C4"
        chordNotes = Chord.chord_notes_from_formula(rootPitch, formula, inversion=0)    # each is amusic21.note.Note
        s = [f"{n.nameWithOctave} " for n in chordNotes]
        print(f"chord notes: {s}")
        c:chord.Chord = chord.Chord(chordNotes)
        c.show(ChordTest.show_format,  root="C4", note_duration="whole")
        
    def test_chord_notes_from_intervals_1(self):
        intervals = ["m3", "m3", "M3"]
        print(f"\n****** test get chord notes from intervals 1: {intervals}  ==========================")
        rootPitch = "C4"
        chordNotes = Chord.chord_notes_from_intervals(rootPitch, intervals, inversion=0)    # each is amusic21.note.Note
        s = [f"{n.nameWithOctave} " for n in chordNotes]
        print(f"chord notes: {s}")
        c:chord.Chord = chord.Chord(chordNotes)
        c.show(ChordTest.show_format,  root="C4", note_duration="whole")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()