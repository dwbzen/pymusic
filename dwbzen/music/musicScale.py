
from music21 import stream, key, note
import pandas as pd

class MusicScale(object):
    def __init__(self,  resource_folder ="/Compile/dwbzen/resources/music", \
                 scale_name='Major', root_note=note.Note('C4'), key=key.Key('C')):
        
        self.scales_df = pd.read_json(resource_folder + "/commonScaleFormulas.json", orient='records').transpose()
        self.scale = self.scales_df.loc[scale_name]
        self.root = root_note
        self.scale_name = scale_name
        self.formula = self.scale['formula']
        self.key = key
        self.notes_stream = None
        self.scale_notes = self.get_scale_notes(root_note)
        self.scale_notes_names = [x.nameWithOctave for x in self.scale_notes]
        self.range_notes = self.get_range_notes(root_note)
        self.range_notes_names = [x.nameWithOctave for x in self.range_notes]
        
    def get_scale_notes(self, start_note=None):
        '''The notes of the configured scale spanning a single octave, for example 'C4' to 'C5'
            Note that the top note is the same as the bottom note but an octave higher.
            Returns: a [Note]
        '''
        ns = stream.Stream()
        ns.append(self.key)
        if start_note is None:
            n = self.root
        else:
            n = start_note
        ns.append(n)
        for i in range(len(self.formula)):
            n = n.transpose(self.formula[i], inPlace=False)
            ns.append(n)
        return [x for x in ns.notes]
    
    def get_range_notes(self, start_note=None, start_octave=0, end_octave=8):
        '''For example, with default arguments notes (Major scale) are C0,D0,...B7,C8
        
        '''
        if start_note is None:
            n = self.root
            start_note = self.root
        else:
            n = start_note
        notes_list = []
        for octave in range(start_octave, end_octave):
            for n in self.scale_notes[:-1]:
                new_note = note.Note(n.name+str(octave))
                notes_list.append(new_note)
        new_note = note.Note(start_note.name+str(end_octave))
        notes_list.append(new_note)
        return notes_list
    
    def get_note(self, scale_degrees:int=0, from_note=None) -> note.Note:
        '''Gets a new Note that is the given scale_degrees away from a given Note.
            Arguments:
                scale_degrees - any integer, the sign dictates the direction - up or down
                from_note - the starting note, default is the scale root note
            Returns: a new Note
            Note if from_note is not present in the full range of notes (self.range_notes), the from_note is returned.
        '''
        if from_note is None:
            from_note = self.root

        if from_note.nameWithOctave in self.range_notes_names:
            ind = self.range_notes_names.index(from_note.nameWithOctave) + scale_degrees
            return self.range_notes[ind]
        else:
            return from_note
