# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       PartsProducer class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import music, common
import pandas as pd
import random
from music21 import note, clef, stream, interval, tempo, meter, key

class MusicProducer(common.Producer):
    """Produce music from interval or notes MarkovChains
    
    TODO: fix reading csv format chains. Currently using the row# as the index which is incorrect. The column lable is "KEY"
    TODO: fix reading durations_chain in json format. Currenly the columns are interpreted as datetime values, should be int.
    
    """

    # TODO - consider making the dataframe keys a list instead of a str of a list
    #
    def __init__(self, state_size, markovChain, durationsChain, source_file, parts, produceParts, num, verbose=0, rand_seed=42, producerType=None):
        super().__init__(state_size, markovChain, source_file, num=num, verbose=verbose,  rand_seed=rand_seed)
        self.instruments = music.Instruments(self.verbose)
        self.show = None
        self.producerType = producerType
        self.save_folder="/Compile/dwbzen/resources/music"
        self.score = stream.Score()
        self.parts = parts                  # comma-delimited filter part names from the command line
        self.produceParts = produceParts    # comma-delimited production part names (instruments) from the command line
        self.part_names, self.part_numbers = MusicProducer.get_parts(parts)
        self.producePart_names = produceParts
        
        self.durationsChain = durationsChain
        self.durationKeys = pd.Series(self.durationsChain.chain_df.index)
        self.durations_key_values = self.durationKeys.values
        
        # if not None, this is the duration to use for all Notes instead of using durationsChain
        self.fixed_duration = None   # duration.Duration(quarterLength=0.5)
        
        self.initial_keys = self.get_initial_keys()
        self.key_values = self.keys.values
        self.raw_seed = None
        self.score_key = key.Key('C')

        #
        # for producerType of 'intervals' there needs to be one start note per part
        #
        self.start_notes = dict()    # key is producePart name, value is a note.Note

        self.tempo = tempo.MetronomeMark(number=60, referent=note.Note(type='quarter'))
        self.timeSignature = meter.TimeSignature('3/4')
        self.num_measures = self.num        # number of measures to produce
        self.enforceRange = False
    
    @staticmethod
    def get_parts(parts:str) -> ([str],[int]):
        part_names = []
        part_numbers = []
        if parts is not None:
            parts_list = parts.split(",")   # could be numbers or names
            for p in parts_list:
                if p.isdigit():   # all digits
                    part_numbers.append(int(p))
                else:
                    part_names.append(p)
        return (part_names, part_numbers)
    

    def __str__(self):
        return f"MusicProducer order={self.order}, source={self.source_file}, num={self.num}, producerType={self.producerType}, \
parts={self.parts}, produce={self.produceParts}, verbose={self.verbose}"

    def add_part_notes(self, notes:str):
        if notes is None:
            raise TypeError("You must specify a starting note for each part")
        notes_list = notes.split(",")
        if len(notes_list) < len(self.producePart_names):    # it's okay to have more notes than parts, just use what's there
            raise TypeError("You must specify a starting note for each part")
        for i in range(len(self.producePart_names)):
            self.start_notes[self.producePart_names[i]] = note.Note(notes_list[i])
    
    def get_initial_keys(self):
        initstr = None
        if self.producerType.startswith('interval'):
            initobj = music.IntervalCollector.initial_object
            initstr = '[{}'.format(initobj.semitones)
        elif self.producerType.startswith('note'):
            initstr="['rest'"
            
        self.initial_keys = self.keys[self.keys.apply(lambda x: x.startswith(initstr))]
        
        return self.initial_keys

    def get_seed(self, aseed=None):
        if self.seed is None or aseed is None or len(self.raw_seed)!=self.order:
            # need to pick one at random
            if self.initial:
                # pick a seed that starts a Part
                theseed = self.initial_keys[random.randint(0, len(self.initial_keys)-1)]
            else:
                # pick any old seed from the chain's index
                theseed = self.keys[random.randint(0, len(self.keys)-1)]
        else:
            theseed = aseed
        return theseed
    
    def get_durations_seed(self):
            # pick any old seed from the durations chain's index
            return self.durationKeys[random.randint(0, len(self.durationKeys)-1)]
        
    def set_seed(self, theseed):
        if self.producerType == 'notes':
            self.raw_seed = theseed.replace(" ","").replace("'","").split(',')
        elif self.producerType == 'intervals':
            self.raw_seed = [int(x) for x in theseed.split(',')]
        self.seed = str(self.raw_seed)

    def get_next_seed(self):
        """
        Checks the seed_count against the recycle_seed_count
        and if >= gets a new seed, otherwise returns the existing one
        """
        self.seed_count = self.seed_count + 1
        aseed = self.seed
        if self.seed_count >= self.recycle_seed_count:
            # pick a new seed
            aseed = self.get_seed()
            self.seed_count = 0
        return aseed
    
    def get_next_object(self, seed):
        """Gets the next Note or Interval based on the seed argument
        
        Args:
            seed: The seed value to look up in the MarkovChain.
        
        Returns:
            Both the next Note or Interval and a new seed as a dict with keys 'new_seed' and 'next_token'
            The type of the next object returned is determined by self.type ('Notes' or 'Intervals')
        """
        
        new_seed = None
        next_token = None
        if self.verbose > 2:
            print(f"get_next_object(seed): '{seed}'")
        if seed in self.key_values:
            row = self.chain_df.loc[seed]
            row_probs = row[row > 0].cumsum()
            # given a probability, pick the first entry in the row_probs (cumulative probabilities)
            # having a probability > the random probability
            # 
            prob = random.random()
            p = row_probs[row_probs> prob].iat[0]
            next_token = int(row_probs[row_probs> prob].index[0])
            if self.producerType == 'intervals':
                ns = [int(x) for x in seed[1:len(seed)-1].split(',')]
            else:   # 'notes'
                ns = seed.strip('[]').replace(" ","").replace("'","").split(',')
                
            ns.append(next_token)
            new_seed = str(ns[1:])
            if self.verbose > 1:
                print(f"random prob: {prob}, row prob: {p}, seed: '{seed}', next_token: '{next_token}', new_seed: '{new_seed}'")
        
        return dict([ ('next_token', next_token), ('new_seed',new_seed)])
    
    def get_next_durations_object(self, seed):
        """Gets the next Duration based on the seed argument
        
        Args:
            seed: The seed value to look up in the durations MarkovChain.
        
        Returns:
            Both the next duration and a new seed as a dict with keys 'new_seed' and 'next_token'
            The type of the next object returned is determined by self.type ('Notes' or 'Intervals')
            
            self.fixed_duration is not None, that is returned as 'next_token'
            and the seed argument is returned as 'new_seed'
        """
        new_seed = None
        next_token = None
        if self.verbose > 2:
            print(f"get_next_object(seed): '{seed}'")
        if self.fixed_duration is not None:
            next_token = self.fixed_duration
            new_seed = seed
        else:
            if seed in self.durations_key_values:
                row = self.durationsChain.chain_df.loc[seed]
                row_probs = row[row > 0].cumsum()
                # given a probability, pick the first entry in the row_probs (cumulative probabilities)
                # having a probability > the random probability
                # 
                prob = random.random()
                p = row_probs[row_probs> prob].iat[0]
                next_token = row_probs[row_probs> prob].index[0]
                ns = [float(x) for x in seed[1:len(seed)-1].split(',')]
                ns.append(next_token)
                new_seed = str(ns[1:])
                if self.verbose > 1:
                    print(f"random prob: {prob}, row prob: {p}, seed: '{seed}', next_token: '{next_token}', new_seed: '{new_seed}'")
                    
        return dict([ ('next_token', next_token), ('new_seed',new_seed)])
        
    def produce(self):
        """Produce a Score from a MarkovChain for producerType == 'intervals'

        """
        
        initial_seed = self.get_seed(self.seed)      # get the initial seed
        seed = initial_seed
        durations_seed = self.get_durations_seed()
        if self.verbose > 0:
            print(f"initial seeds: '{seed}' duration: {durations_seed}")
        if self.verbose > 1:
            print(f" MarkovChain:\n {self.markovChain}")

        # partNotes_dict = dict()     # key is part name, value is [note.Notes]
        #
        # total duration in quarter lengths of all measures
        #
        total_duration = self.num_measures * self.timeSignature.numerator * self.timeSignature.beatDuration.quarterLength
        
        for pname in self.producePart_names:    # the part name must also be an Instrument
            part = stream.Part()
            clef = self.instruments.get_instrument_clef(pname)
            part_instrument = self.instruments.get_instrument(pname)

            part.insert(clef)
            part.insert(self.tempo)
            part.insert(part_instrument)
            part.insert(self.score_key)
            part.insert(self.timeSignature)
            part_notes = []
            part_duration = 0       # running total of the durations of all the part notes
            more_to_go = True
            num_notes = 1
            first_note = self.start_notes[pname]
            part_notes.append(first_note)
            durations_seed = self.get_durations_seed()
            prev_note = self.start_notes[pname]
            while more_to_go:       # more to go for this part
                next_object_dict = self.get_next_object(seed)
                next_duration_dict = self.get_next_durations_object(durations_seed)
                if self.verbose > 1:
                    print('next_token: {}\t new_seed: {}'.format(next_object_dict['next_token'], next_object_dict['new_seed']))
                #
                # create the next note
                #
                halfsteps = next_object_dict['next_token']
                if halfsteps == 100:
                    #
                    # if the next token is the terminal object (100 in this case)
                    # pick a new seed and continue
                    #
                    seed = self.get_seed()
                    continue
                ainterval = interval.Interval(halfsteps)
                if self.verbose > 2:
                    print(f"halfsteps: {halfsteps}, interval: {ainterval}")
                
                dur = next_duration_dict['next_token']    # quarterLength 
                if dur is None:
                    durations_seed = self.get_durations_seed()
                    continue             
                newnote = prev_note.transpose(ainterval)
                if self.enforceRange and not self.instruments.is_in_range(pname, newnote):
                    steps_out_of_range = self.instruments.check_range(pname, newnote)
                    #
                    # if the note is out of range for this part (instrument)
                    # transpose up an octave is below the range, down an octave if above
                    if self.verbose > 0:
                        print(f"newnote: {newnote.nameWithOctave} out of range for {pname}, by {steps_out_of_range} steps")
                    if steps_out_of_range <0:
                        tintval = interval.Interval('P8')
                    else:
                        tintval = interval.Interval('P-8')
                    newnote = newnote.transpose(tintval)
                                            
                remaining_dur =  total_duration - part_duration
                if part_duration + dur >= total_duration:
                    dur = remaining_dur     # make the last note fill out the measure
                    more_to_go = False
                if dur > 0:
                    newnote.duration.quarterLength = dur
                    if self.verbose > 1:
                        print(f"{newnote.fullName}")
                    part_notes.append(newnote)
                    
                    part_duration = part_duration + dur
                    prev_note = newnote
                    seed =  next_object_dict['new_seed']
                    durations_seed = next_duration_dict['new_seed']
                    num_notes = num_notes + 1
            
            #
            # add rests to pad the last measure(s) of each part
            # so all parts have the same total duration (in terms of quarter lengths)
            # 
            if self.verbose > 0:
                print(f"---- End of {pname} part, duration: {part_duration}")
            part.append(part_notes)
            self.score.append(part)
    
        return self.score
    
    
    if __name__ == '__main__':
        print(MusicProducer.__doc__)
        
        