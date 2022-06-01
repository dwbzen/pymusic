# ------------------------------------------------------------------------------
# Name:          producer.py
# Purpose:       PartsProducer class.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2021 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------

import music
from common.producer import Producer
from music.musicUtils import MusicUtils
import pandas as pd
import random, math, sys
from music21 import note, clef, stream, interval, tempo, meter, key, metadata

class MusicProducer(Producer):
    """Produce music from interval or notes MarkovChains

    Known Issues: 
      Reading durations_chain in json format is incorrect. Currently the columns are interpreted as datetime values, should be int.
      MusicProducer intervals on existing chain file gets into an infinite loop. With the same parameters creating the chain files works fine.

    """

    def __init__(self, state_size, markovChain, durationsChain, source_file, parts, produceParts, num=10, verbose=0, rand_seed=42, producerType=None):
        super().__init__(state_size, markovChain, source_file, num=num, verbose=verbose,  rand_seed=rand_seed)
        
        self.instruments = music.Instruments(self.verbose)
        self.show = None
        self.producerType = producerType

        self.score = stream.Score()
        self.score.insert(0, metadata.Metadata())
        self.parts = parts                  # comma-delimited filter part names from the command line
        self.produceParts = produceParts    # comma-delimited production part names (instruments) from the command line
        self.part_names, self.part_numbers = MusicProducer.get_parts(parts)
        self.producePart_names = produceParts
        
        self.durationsChain = durationsChain

        
        # if not None, this is the duration to use for all Notes instead of using durationsChain
        self.fixed_duration = None   # duration.Duration(quarterLength=0.5)
        
        self._set_keys()
        self.raw_seed = None
        self.score_key = key.Key('C')

        #
        # for producerType of 'intervals' there needs to be one start note per part
        #
        self.start_notes = dict()    # key is producePart name, value is a note.Note

        #
        # for producerType of 'notes' need to have the collection mode (dp, dpc, ap, apc)
        #
        self.collection_mode = None
        self.tempo = tempo.MetronomeMark(number=80, referent=note.Note(type='quarter'))
        self.timeSignature = meter.TimeSignature('4/4')
        self.num_measures = self.num        # number of measures to produce
        self.enforceRange = False           # force instruments to their range
        self.trace_mode = False             # displays the notes/intervals as they are produced
    
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
        notes_list = []
        if notes is None:
            if self.producerType == 'intervals':
                raise TypeError("You must specify a starting note for each part")
            else:
                # need n-starting notes where n is the number of producePart_names
                notes_list = self.get_seed(aseed=None)
        else:      
            notes_list = notes.split(",")
        if len(notes_list) < len(self.producePart_names):    # it's okay to have more notes than parts, just use what's there
            raise TypeError("You must specify a starting note for each part")
        
        for i in range(len(self.producePart_names)):
            self.start_notes[self.producePart_names[i]] = note.Note(notes_list[i])
    
    def _set_keys(self):
        initstr = None
        if self.producerType == 'intervals':
            initobj = music.IntervalCollector.initial_object
            initstr = '{}'.format(initobj.semitones)
        elif self.producerType == 'notes':
            initstr="'C0'"
        
        self._keys = pd.Series(self.chain_df.index)
        self._key_values = self._keys.values
        self._initial_keys = self._keys[self._keys.apply(lambda x: x.startswith(initstr))]
        
        self._durationKeys = pd.Series(self.durationsChain.chain_df.index)
        self._durations_key_values = self._durationKeys.values

    def get_seed(self, aseed=None):
        theseed = self.seed
        if self.seed is None:
            # no seed already exists, so use the aseed argument if it's not None or pick one at random
            if aseed is not None:
                theseed = aseed
            elif self.initial:
                # pick a seed that starts a Part
                ind = random.randint(0, len(self.initial_keys)-1)
                theseed = self.initial_keys.iloc[ind]
            else:
                # pick any old seed from the chain's index
                ind = random.randint(0, len(self.keys)-1)
                theseed = self.keys.iloc[ind]
        return theseed
    
    def get_durations_seed(self):
            # pick any old seed from the durations chain's index
            return self._durationKeys[random.randint(0, len(self._durationKeys)-1)]
        
    def set_seed(self, raw_seed, collector_type):
        """Creates a seed for Notes or Intervals from a list
            Arguments:
                raw_seed - a [str] or [int] depending on collector_type
                collector_type - 'notes' or 'intervals'
            Returns:
                For collector_type of notes, the input is a [str], for example: ['A4', 'G4'],
                the result is a single string "A4,G4" in this case.
                For collector_type of intervals, the input is a [int], for example [-2, -1]
                the result is a single string, "-2,-1" in this case
        
        """
        if collector_type == "intervals":
            theseed = MusicUtils.to_string(raw_seed)
        elif collector_type == "notes":
            theseed = ",".join(raw_seed)
        
        self.seed = theseed
        return self.seed

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
        if self.trace_mode:
            print(f"get_next_object(seed): \"{seed}\"")
        if seed in self._key_values:
            row = self.chain_df.loc[seed]
            row_probs = row[row > 0].cumsum()
            # given a probability, pick the first entry in the row_probs (cumulative probabilities)
            # having a probability > the random probability
            # 
            prob = random.random()
            p = row_probs[row_probs> prob].iat[0]
            nt = row_probs[row_probs> prob].index[0]
            
            if self.producerType == 'intervals':    # intervals can only be integers (for now)
                ns = [int(x) for x in seed.split(',')]
                next_token = int(math.trunc(float(nt)))
            else:   # 'notes'
                ns = seed.split(',')
                next_token = nt
                
            ns.append(next_token)
            new_seed =  MusicUtils.to_string(ns[1:])
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
            
        TODO - this doesn't work for order=1 chains, and it looks like it only works for order=2
        get_next_object probably has same problem.
        The problem is the durations chain keys for order 1 is a float instead of a string.
        
        """
        new_seed = None
        next_token = None
        if self.trace_mode:
            print(f"get_next_durations_object(seed): \"{seed}\"")
        if self.fixed_duration is not None:
            next_token = self.fixed_duration
            new_seed = seed
        else:
            if seed in self._durations_key_values:
                row = self.durationsChain.chain_df.loc[seed]
                row_probs = row[row > 0].cumsum()
                # given a probability, pick the first entry in the row_probs (cumulative probabilities)
                # having a probability > the random probability
                # 
                prob = random.random()
                p = row_probs[row_probs> prob].iat[0]
                next_token = float(row_probs[row_probs> prob].index[0])
                #
                # this next bit is needed because order=1 duration chain index (seed variable) is float instead of str
                # so it's a hack until that can be fixed
                #
                if isinstance(seed, float):
                    ns = seed   # a single float value
                    new_seed = next_token
                else:
                    ns = [float(x) for x in seed.split(',')]
                    ns.append(next_token)
                    new_seed = str(ns[1:]).replace(' ', '')
                    new_seed = new_seed[1:len(new_seed)-1]   # drop the []
                    
                if self.verbose > 1:
                    print(f"random prob: {prob}, row prob: {p}, seed: '{seed}', next_token: '{next_token}', new_seed: '{new_seed}'")
                    
        return dict([ ('next_token', next_token), ('new_seed',new_seed)])
    
    
    def produce(self):
        """Produce a Score from a MarkovChain
        
        """
        
        initial_seed = self.get_seed(self.seed)      # get the initial seed
        seed = initial_seed
        durations_seed = self.get_durations_seed()
        if self.verbose > 0:
            print(f"initial seeds: '{seed}' duration: {durations_seed}")
        if self.verbose > 2:
            print(f" MarkovChain:\n {self.markovChain}")
        #
        # partNotes_dict = dict(),  key is part name, value is [note.Note]
        #
        # total duration is sum of quarter lengths of all measures
        #
        total_duration = self.num_measures * self.timeSignature.numerator * self.timeSignature.beatDuration.quarterLength
        
        for pname in self.producePart_names:    # the part name must also be a valid Instrument
            if self.verbose > 0:
                print(f"---- Starting {pname} part")            
            part = stream.Part()
            clef = self.instruments.get_instrument_clef(pname)
            part_instrument = self.instruments.get_instrument(pname)

            part.insert(clef)
            part.insert(self.tempo)
            part.insert(part_instrument)
            part.insert(self.score_key)
            part.insert(self.timeSignature)
            part_notes = []
            
            if self.producerType == 'intervals':
                part_notes = self.produce_intervals(pname, seed, total_duration)
            elif self.producerType == 'notes':
                part_notes = self.produce_notes(pname, seed, total_duration)
            
            #
            # add rests to pad the last measure(s) of each part
            # so all parts have the same total duration (in terms of quarter lengths)
            # 
            if self.verbose > 0:
                print(f"---- End of {pname} part")
            part.append(part_notes)
            self.score.append(part)
        
        return self.score
    
    def produce_notes(self, part_name, seed, total_duration):
        """Produce a list of Note from a MarkovChain for 'notes' producerType for the named part

        """        
        part_notes = []
        more_to_go = True
        num_notes = 0
        part_duration = 0.0  # running total of the durations of all the part notes
        durations_seed = self.get_durations_seed()

        terminal_note = music.NoteCollector.terminal_object     # 'C#8'
            
        while more_to_go:       # more notes to add for this part
            next_object_dict = self.get_next_object(seed)
            next_duration_dict = self.get_next_durations_object(durations_seed)
            newnote_str = next_object_dict['next_token']
            newnote = note.Note(newnote_str)
            if self.trace_mode:
                print('newnote: {}\t new_seed: {}'.format(newnote.nameWithOctave, next_object_dict['new_seed']))
            if newnote == terminal_note:
                seed = self.get_seed()
                continue

            dur_str = next_duration_dict['next_token']    # quarterLength 
            if dur_str is None:
                durations_seed = self.get_durations_seed()
                continue
            dur = float(dur_str)
            if self.enforceRange and not self.instruments.is_in_range(part_name, newnote):
                #
                # if the note is out of range for this part (instrument)
                # transpose up/down the number of octaves needed to bring back into range
                #
                self.instruments.adjust_to_range(part_name, newnote, inPlace=True)

            remaining_dur =  total_duration - part_duration
            if part_duration + dur >= total_duration:
                dur = remaining_dur     # make the last note fill out the measure
                more_to_go = False
            if dur > 0:
                #
                # add rests to pad the last measure(s) of each part
                # so all parts have the same total duration (in terms of quarter lengths)
                #                 
                newnote.duration.quarterLength = dur
                if self.verbose > 1:
                    print(f"{newnote.fullName}")
                part_notes.append(newnote)

                part_duration = part_duration + dur
                seed =  next_object_dict['new_seed']
                if seed is None:
                    print("seed is None")
                durations_seed = next_duration_dict['new_seed']
                num_notes = num_notes + 1
                
        if self.verbose > 0:
            print(f"---- End of {part_name} part, duration: {part_duration}")
                    
        return part_notes
    
    def produce_intervals(self, part_name, seed, total_duration):
        """Produce list of Note from a MarkovChain for 'intervals' producerType for the named part

        """
        
        part_notes = []
        more_to_go = True
        num_notes = 1
        first_note = self.start_notes[part_name]
        part_notes.append(first_note)
        part_duration = first_note.duration.quarterLength       # running total of the durations of all the part notes
        durations_seed = self.get_durations_seed()
        prev_note = self.start_notes[part_name]
        
        while more_to_go:       # more notes to add for this part
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
            if self.trace_mode:
                print(f"halfsteps: {halfsteps}, interval: {ainterval.name}")
            
            dur_str = next_duration_dict['next_token']    # quarterLength 
            if dur_str is None:
                durations_seed = self.get_durations_seed()
                continue
            dur = float(dur_str)
            if prev_note is None:
                print("Warning: prev_note is None", file=sys.stderr)
                continue
                
            newnote = prev_note.transpose(ainterval)
            if self.enforceRange and not self.instruments.is_in_range(part_name, newnote):
                #
                # if the note is out of range for this part (instrument)
                # transpose up/down the number of octaves needed to bring back into range
                #
                self.instruments.adjust_to_range(part_name, newnote, inPlace=True)

            remaining_dur =  total_duration - part_duration
            if part_duration + dur >= total_duration:
                dur = remaining_dur     # make the last note fill out the measure
                more_to_go = False
            if dur > 0:
                #
                # add rests to pad the last measure(s) of each part
                # so all parts have the same total duration (in terms of quarter lengths)
                #                 
                newnote.duration.quarterLength = dur
                if self.verbose > 1:
                    print(f"{newnote.fullName}")
                part_notes.append(newnote)

                part_duration = part_duration + dur
                prev_note = newnote
                seed =  next_object_dict['new_seed']
                durations_seed = next_duration_dict['new_seed']
                num_notes = num_notes + 1    

        if self.verbose > 0:
            print(f"---- End of {part_name} part, duration: {part_duration}")
    
        return part_notes
    
    
if __name__ == '__main__':
    print(MusicProducer.__doc__)
        
        