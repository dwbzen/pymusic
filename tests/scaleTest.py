'''
Created on Aug 22, 2026

@author: don_bacon
'''

import unittest
from music.scale import Scale, Notes
from music.scales import Scales
from music.keys import Keys
from music.key import  Key

class ScaleTest(unittest.TestCase):
    
    keys = Keys()
    key_name = "C-Major"
    key:Key = keys.key(key_name)
    scales = Scales(key)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_scale1(self):
        scale_name = "Harmonic Major 1"
        print(f"\n****** test create {scale_name} Scale, ascending, 1 octave, C-Major key ==========================")
        scale_data = ScaleTest.scales.scaleLib.getScaleData(scale_name)
        key = ScaleTest.keys.key("C-Major")
        root=key.tonic
        scale = Scale(scale_data, key=key)
        print(scale.pitches(root))
        print(scale.notes(root))
    
    def test_get_scale2(self):
        scale_name = "Melodic minor ascending"
        print(f"\n****** test create {scale_name} Scale, 1 octave, F-Minor key ==========================")
        key = ScaleTest.keys.key("F-Minor")
        root=key.tonic
        scale = ScaleTest.scales.get_scale(scale_name, key, octaves=1, descending=False)
        print(scale.pitches(root))
        print(scale.notes(root))
        
    def test_get_scale_two_octaves_ascending(self):
        scale_name = "Pentatonic minor"
        key = ScaleTest.keys.key("F-Minor")
        noctaves = 2
        start_octave = 3
        print(f"\n****** test create {scale_name} Scale, {noctaves} octaves, key of {key.key_name} ascending ==========================")
        root=f"{key.tonic}{start_octave}"
        scale = ScaleTest.scales.get_scale(scale_name, key, octaves=noctaves, descending=False)
        pitches = scale.pitches(root=root, octaves=noctaves)
        print(f"pitches: {pitches}")
        notes = scale.notes(root=root, num_octaves=noctaves)
        print(f"notes: {notes}")
        scale.show("musicxml.png", notes=notes)

    def test_get_scale_two_octaves_descending(self):
        scale_name = "Persian"  # "Blues Minor"
        key = ScaleTest.keys.key("C-Minor")
        noctaves = 2
        print(f"\n****** test create {scale_name} Scale, {noctaves} octaves, key of {key.key_name} descending ==========================")
        root=key.tonic
        scale = ScaleTest.scales.get_scale(scale_name, key, octaves=noctaves, descending=True)
        pitches = scale.pitches(root=root, octaves=noctaves)
        print(f"pitches: {pitches}")
        notes = scale.notes(root=root, num_octaves=noctaves)
        print(f"notes: {notes}")
        scale.show("musicxml", notes=notes, note_duration="eighth")
        

    def test_get_chromatic_pitches(self):
        print(f"\n****** test get_chromatic pitches, pitches only ==========================")
        notes = Notes()
        cp = notes.chromatic_pitches
        cpf = cp["flat"]
        cps = cp["sharp"]
        cpm = cp["mixed"]
        print(f"len: {len(cpf)}, {len(cps)}")
        #assert(len(cpf)==12*num_octaves)
        assert(len(cpf)==len(cps))
        print(f'chromatic flats: {cpf}')
        print(f'chromatic sharps: {cps}')
        print(f'chromatic mixed: {cpm}')

    def test_get_chromatic_notes(self):
        notes = Notes()
        print(f"\n****** test get_chromatic notes (pitches with octave) ==========================")
        cp = notes.chromatic_notes
        cpf = cp["flat"]
        cps = cp["sharp"]
        cpm = cp["mixed"]
        print(f"len: {len(cpf)}, {len(cps)}")
        #assert(len(cpf)==12*num_octaves)
        assert(len(cpf)==len(cps))
        print(f'chromatic flats: {cpf}')
        print(f'chromatic sharps: {cps}')
        print(f'chromatic mixed: {cpm}')
    
    def test_get_note_numbers(self):
        notes = Notes()
        print(f"\n****** test test_get_note_numbers for notes (pitches with octave) ==========================")
        # note that D4 appears twice in the list below. Only 1 dict entry is therefore created
        #
        notes_list = ("A0", "C1", "F#2", "Bb3", "D4", "G#7", "B10", "C##", "Dbb")
        note_numbers = notes.get_note_number(*notes_list)
        print(f"note numbers map: {note_numbers}")
        assert(len(note_numbers)==8)
        vals = list(note_numbers.values())
        print(f"note numbers: {vals}")
    
    def xtest_enharmonic_equivalent(self):
        print(f"\n****** test enharmonic_equivalent pitches, no octaves ==========================")
        sharps = [f"{p}#" for p in Notes.NATURAL_PITCHES]    # C,D,...B
        sharps_answers = ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C"]
        flats =  [f"{p}b" for p in Notes.NATURAL_PITCHES]
        flats_answers = ["B", "C#", "D#", "E", "F#", "G#", "A#"]
        for i in range(7):
            p = sharps[i]
            ee = Scale.enharmonic_equivalent(p)    # duple
            print(f"{p} = {ee}")
            assert(ee[0]==sharps_answers[i])
            p = flats[i]
            ee = Scale.enharmonic_equivalent(p)    # duple
            print(f"{p} = {ee}")
            assert(ee[0]==flats_answers[i])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()