
from common import RuleSet
from music import MusicScale, Instruments
from music21 import stream, instrument, clef, key, meter
from music21 import note, tempo, metadata


class ScoreGen(object):
    
    def __init__(self, rule_set:RuleSet, resource_folder ="/Compile/dwbzen/resources/music", verbose=0, \
                 scale_name='Major', instrument_name='Soprano', key=key.Key('C'), title="Music Substiution" ):
        '''
            TODO - allow for more than 1 part (instrument). There needs to be a list of start notes,
            one for each part. instrument_name also needs to be a list.
        '''
        self.resource_folder = resource_folder
        self.scale_name = scale_name
        self.rule_set = rule_set
        self.verbose = verbose
        self.instrument_name = instrument_name
        #
        # create score metadata
        #
        self.tempo = tempo.MetronomeMark(number=100, referent=note.Note(type='quarter'))
        self.timeSignature = meter.TimeSignature('4/4')
        
        self.score = stream.Score()
        self.score.insert(0, metadata.Metadata())
        self.score.metadata.title = title
        
        self.part = stream.Part()    # the part created from pitch rules
        self.part.partName = instrument_name
        self.instruments = Instruments()
        self.instrument = self.instruments.instruments_pd.loc[instrument_name]
        clef = self.instruments.get_instrument_clef(instrument_name)
        self.part.insert(clef)
        self.part.insert(self.tempo)
        self.part.insert(instrument.Instrument(instrumentName=instrument_name))
        self.key = key
        self.part.insert(key)
        self.part.insert(self.timeSignature)
        
        self.state = dict()
        self.command_rules = rule_set.rules['commands']
        self.notes = []   # all the notes added

    def run(self, commands:[str], start_note=note.Note("C5", quarterLength=2)) -> stream.Score:
        '''The start_note must have a pitch with octave and a duration in quarterLengths
        
        ''' 
        self.musicScale = MusicScale(resource_folder=self.resource_folder, scale_name=self.scale_name, root_note=start_note)
        self.scale = self.musicScale.scale
        self.start_note = start_note
        
        self.state['note'] = start_note
        self.state['previous_note'] = None
        self.state['musicScale'] = self.musicScale
        self.state['instruments'] = self.instruments
        self.state['instrument_name'] = self.instrument_name
        
        self.apply_commands(commands)
        self.score.append(self.part)
        return self.score

    def apply_commands(self, commands):
        '''Creates the Part notes from the commands string by executing the associated rules
            Sample commands: ['0/0.5', '+1/1.0', '-2/1.0', '+1/2.0', '+1/0.5', '0/duration', '0/1.0', '1/0.5']
        '''
        for command in commands:
            self.apply_command(command)
    
    def apply_command(self, command):
        if self.verbose > 0:
            print(f'Command: {command} -------------------------')
        group_dict = self.rule_set.splitter.match(command)
        if group_dict is None:
            return None
        interval = group_dict['interval']
        duration =  group_dict['duration']
        int_rule = self.command_rules['interval']
        dur_rule = self.command_rules['duration']
        int_rule(interval, self.state)    # apply to state['note']
        next_note = dur_rule(duration, self.state)    # apply to state['note']
        self.notes.append(next_note)
        self.part.append(next_note)

    