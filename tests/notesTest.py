'''
Created on Oct 28, 2026

@author: dwbze
'''
import unittest
from music.notes import Notes


class NotesTest(unittest.TestCase):

    NOTES = Notes()

    def test_getChromaticNotes(self):
        notes = NotesTest.NOTES
        chromatic_notes = notes.chromatic_notes
        chromatic_pitches = notes.chromatic_pitches
        print(chromatic_notes["sharp"])
        print(chromatic_pitches["flat"])
    
    def test_getNote_PitchNumbers(self):
        notes = NotesTest.NOTES
        anote1 = "D3"
        anote2 = "F#4"
        note_numbers = notes.get_note_number(anote1, anote2)
        assert note_numbers["D3"] == 38 and note_numbers["F#4"] == 54
        pitch1 = "A"
        pitch2 = "D"
        pitch_numbers = notes.get_pitch_number(pitch1,pitch2)
        print(f" {anote1}, {anote2}  note numbers: {note_numbers}")
        print(f" {pitch1}, {pitch2} pitch numbers: {pitch_numbers}")
        
    def test_noteDistance(self):
        notes = NotesTest.NOTES
        anote1 = "D3"
        anote2 = "F#4"
        dist1 = notes.distance(anote1, anote2)
        dist2 = notes.distance(anote2, anote1)
        print(f"distance from {anote1} to {anote2}: {dist1}")    # 16 is the right answer
        print(f"distance from {anote2} to {anote1}: {dist2}")    # -16
    
    def test_compareNotes_Pitches(self):
        notes = NotesTest.NOTES
        anote1 = "D3"
        anote2 = "F#4"
        pitch1 = "A"
        pitch2 = "D"
        print(f"\n****** test_compareNotes_Pitches {anote1} {anote2}, {pitch1} {pitch2} ==========================")
        compared = notes.compare_notes(anote1, anote2)
        print(f"comparing {anote1}, {anote2}: {compared}")
        
        compared = notes.compare_pitches(pitch1, pitch2)
        print(f"comparing {pitch1}, {pitch2}: {compared}")
        
        relative_to="F"
        compared = notes.compare_pitches(pitch1, pitch2, relative_to="F")
        print(f"comparing {pitch1}, {pitch2} relative to {relative_to}: {compared}")
    
    def test_getNotes(self):
        notes = NotesTest.NOTES
        anote1 = "D4"
        anote2 = "Db5"
        print(f"\n****** test_getNotes {anote1} {anote2} ==========================")
        note_numbers = notes.get_note_number(anote1, anote2)
        dist = notes.distance(anote1, anote2)
        print(f" {anote1}, {anote2}  note numbers: {note_numbers}, distance: {dist}")
        
        note_list = notes.get_notes(note_numbers[anote1], note_numbers[anote2], num_sharps=2)
        for n in note_list:
            print(n.nameWithOctave)
        assert len(note_list) == dist+1

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()