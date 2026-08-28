'''
Created on Oct 14, 2025

@author: don_bacon
'''
import unittest
from music.musicScale import MusicScale
from music.scale import Scale, Notes
from music21 import key, note

class MusicScaleTest(unittest.TestCase):


    def testMusicScale_1(self):
        print(f"\n****** test MusicScale default arguments ==========================")
        music_scale = MusicScale()
        notes = music_scale.get_scale_notes()
        print(music_scale)
        print(notes)
    
    def testMusicScale_2(self):
        print(f"\n****** test MusicScale get a Hungarian Minor scale ==========================")
        music_scale = MusicScale(scale_name='Hungarian Minor', root_note=note.Note('D4'), key=key.Key('D'),)
        notes = music_scale.get_scale_notes()
        print(music_scale)
        print(notes)
    
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()