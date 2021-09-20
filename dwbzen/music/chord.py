'''
Created on Mar 3, 2021

@author: don_bacon
'''
import json
import music

class Chord(object):

    def __init__(self, raw_data={}):
        '''
        Constructor
        '''
        # print("raw data: {}".format(raw_data))
        if(type(raw_data) is dict):
            self.chord = raw_data
        else:
            self.chord = json.loads(raw_data)
    
        self.name = self.chord['name']
        self.formula = self.chord['formula']
        self.intervals = self.chord['intervals']
        self.notes = self.chord['spelling'].split(' ')
        self.symbols = self.chord['symbols']
        self.size = len(self.formula)
        _scale = {}
        _scale['formula'] = self.formula
        _scale['name'] = self.name
        self.scale = music.Scale(_scale)
        
    
    if __name__ == '__main__':
        print('Sample Chords usage')
        chords_file = "../../resources/allChordFormulas.json"
        _chords = music.Chords(json_file_name = chords_file)
        _chord = _chords.chord['Ninth flat fifth']
        print(_chord.chord)
        print('Ninth flat fifth: {}'.format(_chord.notes))
        
        # get the notes for a different root
        _notes = _chord.scale.notes(root='A', accidental_preference='mixed')
        print(_notes)
        

        