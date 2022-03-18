
from music21 import note, duration
from music21.stream import Score
import copy

class MusicSubstitutionRules(object):
    
    trace = False
    
    @staticmethod
    def show(anote:note.Note):
        print(f"pitch: {anote.nameWithOctave}  duration: {anote.duration.quarterLength}")
    
    @staticmethod
    def score_postprocess(ascore:Score, instrument_name:str):
        '''Checks the pitch against the range of the given instrument, adjusting if necessary.
            TODO
        '''
        if MusicSubstitutionRules.trace:
            print('score_postprocess')
    
    @staticmethod
    def score_preprocess(ascore:Score):
        if MusicSubstitutionRules.trace:
            print('score_preprocess')
    
    @staticmethod
    def interval_rule(sd:str, state):
        anote = state['note']
        instrument_name = state['instrument_name']
        if sd == 'interval':
            scale_degrees = 0
        else:
            scale_degrees = int(sd)
            
        if MusicSubstitutionRules.trace:
            print(f' apply interval {scale_degrees} TO  {anote.nameWithOctave} {anote.duration.quarterLength}')
            
        musicScale = state['musicScale']   # music.MusicScale
        instruments = state['instruments']   # music.Instruments
        note_dur = anote.duration.quarterLength
        scale_note = musicScale.get_note(scale_degrees, anote)
        next_note = copy.deepcopy(scale_note)
        next_note.duration = duration.Duration(note_dur)
        state['previous_note'] = anote
        #
        # check the range of next_note and adjust if needed
        #
        if not instruments.is_in_range(instrument_name, next_note):
            instruments.adjust_to_range(instrument_name, next_note, inPlace=True)
        
        state['note'] = next_note
        #
        return next_note
    
    @staticmethod
    def duration_rule(d:str, state):
        '''Apply the duration command d to Note anote.
            Arguments:
                d - a float to multiply the Notes duration.quarterLength by
                anote - a Note
            Note if the resulting product is >4, it is reduced by half.
            If < 0.125, it is multiplied by 2
        '''
        anote = state['note']
        if d=='duration':
            multiplier = 1.0
        else:
            multiplier = float(d)
            
        if MusicSubstitutionRules.trace:
            print(f' apply duration {multiplier} TO {anote.nameWithOctave} {anote.duration.quarterLength}')
            
        old_dur = anote.duration.quarterLength
        new_dur = round(old_dur * multiplier, 3)
        if new_dur > 4.0:      # the maximum duration is a whole note
            new_dur = 0.5    
        elif new_dur < 0.125:  # the minimum duration is 32nd note
            new_dur = 2.0
            
        new_note = note.Note(anote.nameWithOctave, quarterLength=new_dur)
        if MusicSubstitutionRules.trace:
            print(f"\told_dur: {old_dur}  new_dur: {new_dur}\n")
        state['note'] = new_note
        return new_note
    
    if __name__ == '__main__':
        print("MusicSubstitutionRules")
