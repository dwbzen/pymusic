
from music21 import interval, instrument, corpus, converter
from music21 import note, clef, duration, metadata, key, pitch, scale
from music21.stream import Score
from music21.stream import Part
from music21.stream import Measure
from music.instruments import Instruments

import re
import pandas as pd
import pathlib, random, copy, math
from datetime import date
from builtins import isinstance

class MusicUtils(object):
    """Music utilities
        TODO - the method names are confusing, like score_notes vs. notes_for_score etc. Need to refactor
    """
    
    verbose = 0
    C_Major = key.Key('C')
    A_Minor = key.Key('a')
    default_pitch_map = {'Db':'C#', "D-":'C#', 'D#':'Eb', 'Gb':'F#', 'G-':'F#', 'Ab':'G#', 'A-':'G#', 'A#':'Bb' }
     
    @staticmethod
    def get_score(file_path:str) -> Score:
        score = None
        file_info = MusicUtils.get_file_info(file_path)
        if file_info['exists']:
                score = converter.parse(file_info['path_text'])
        return score
    
    @staticmethod
    def get_score_parts_info(ascore, partnames=None, display=False):
        part_dict = {}
        for apart in ascore.parts:
            if partnames is None or (partnames is not None and apart.partName in partnames):
                ksigs, mnumbers = MusicUtils.get_keySignatures(apart)
                for ks in ksigs:
                    if not isinstance(ks, key.Key):
                        ks = ks.asKey()
                    if display:
                        print(f'  {apart.partName}  {ks} {ks.mode}')
                    part_dict[apart.partName] = {'key':ks, 'keyName':ks.name, 'mode':ks.mode }
        return part_dict
    
    @staticmethod
    def get_parts_info(scores, partnames=None, display=False):
        all_scores = {}
        for ascore in scores:
            title = ascore.metadata.title
            if display: print(title)
            all_scores[title] = MusicUtils.get_score_parts_info(ascore, partnames, display)
        return all_scores
    
    #
    # get intervals for a Part
    #
    @staticmethod
    def get_part_intervals(apart:Part) -> [dict]:
        """Get all intervals for a Part.
        
        Arguments:
            apart - a Part instance
        Returns:
            A list of intervals where each interval is a dict with the keys "note1", "note2"
            the integer interval (number of semitones) needed to go from note1 to note2.
        """
        intrvals = []
        part_notes = apart.flat.getElementsByClass('Note')
        for ind in range(len(part_notes)-1):
            n1 = part_notes[ind]
            n2 = part_notes[ind+1]
            i = interval.Interval(n1, n2)
            idict = {'note1':n1, 'note2':n2, 'interval':i}
            intrvals.append(idict)
        return intrvals
    
    @staticmethod
    def get_part_notes(apart:Part) -> [note.Note]:
        part_notes = apart.flat.getElementsByClass('Note')
        return part_notes
    
    @staticmethod
    def get_scale_degree(akey:key.Key, anoteorpitch:object) -> dict:
        modifier = ''
        apitch = anoteorpitch
        if isinstance(anoteorpitch, note.Note):
            apitch = anoteorpitch.pitch
        sd,accidental = akey.getScaleDegreeAndAccidentalFromPitch(apitch)
        if accidental is not None:
            modifier = accidental.modifier
        sdstr = f'{modifier}{sd}'
        roman = f'{modifier}{akey.romanNumeral(sd).figure}'
        
        return {'pitch':apitch, 'pitch_name':apitch.name, 'number':sdstr, 'roman':roman}

    @staticmethod
    def get_pitch_from_scaleDegree(akey:scale.ConcreteScale, sd:str, octave=None) -> pitch.Pitch:
        """Given a scale degree and a Key, return a deepcopy of the appropriate pitch
        
        The music21 pitchFromDegree api only handles integer scale degrees
        This accepts a string with the scale degree prepended with an accidental #, - or b
        so for example, in Key('C'), "-3" is actually an e- (e-flat)
        "#4" and "-5" are both a F4.
        NOTE that the range of pitches returned is C4 to B4. The octave can be set
        using the optional octave argument.
        """

        p = None
        if sd.isdigit():
            p = akey.pitchFromDegree(int(sd))
        elif len(sd) >= 2:
            accidental = sd[0]
            semitones = 1
            if accidental == '-' or accidental == 'b':
                semitones = -1
            degree = int(sd[1:])
            p = akey.pitchFromDegree(degree)
            p = p.transpose(interval.Interval(semitones))
        if octave is not None:
            p.octave = octave
        return p
    
    @staticmethod
    def get_scale_degrees(apart:Part) -> [dict]:
        """Gets the scale degree of every note's pitch in a given Part
        
        Arguments:
            apart - a music21.stream.Part instance
        Returns:
            a list of dictionary entries for each Part note.
            The keys are 'pitch', 'pitch_name', 'number' and 'roman' (for a Roman figure).
            where 'pitch' is a Pitch object, 'number' and 'roman' are scale degrees as a string.
            Any alterations are indicated by prepending a # or - for sharp, flat.
            An empty list is returned if there is no Key or KeySignature associated with the Part
            
        Note that Chords are not handled. In particular, notes that are part of a Chord are ignored.
        """
        key_sigs,measure_numbers = MusicUtils.get_keySignatures(apart)
        measure_numbers.append(len(apart))
        scale_degrees = []
        for i in range(len(key_sigs)):
            k = key_sigs[i]
            if not isinstance(k, key.Key):
                k = k.asKey()
            partMeasures = apart.measures(measure_numbers[i], measure_numbers[i+1]-1)   # measure range is inclusive
            pNotes = partMeasures.flat.getElementsByClass('Note')
            partPitches = pNotes.pitches
            for p in partPitches:
                scale_degrees.append(MusicUtils.get_scale_degree(k, p))
        return scale_degrees

    @staticmethod
    def get_score_intervals(ascore:Score, partname:str=None) -> dict:
        """ Get the intervals for all Parts of a Score
        
        Arguments:
            ascore - a Score instance
            partname - a part name in the Score or None to get intervals for all parts
        Returns:
            A dictionary of intervals where the key is the part name. The key values
            is a list of intervals where each interval is a dict with the keys "note1", "note2"
            the integer interval (number of semitones) needed to go from note1 to note2.
        """
        parts = ascore.getElementsByClass(Part)
        pdict = dict()
        for p in parts:
            pname = p.partName
            if partname is None or pname==partname:
                pdict[pname] = MusicUtils.get_part_intervals(p)
        return pdict
    
    @staticmethod
    def get_score_notes(ascore:Score, partname:str=None) -> dict:
        """Get the Notes for all Parts or the named part of a Score as a dict with the part name as the key, and a [note.Note] as the value.
        
        Note that this does not return Rest or Chord objects
        """
        parts = ascore.getElementsByClass(Part)
        pdict = dict()
        for p in parts:
            pname = p.partName
            if partname is None or pname==partname:
                notes = MusicUtils.get_part_notes(p)
                pdict[pname] = notes
        return pdict

    @staticmethod
    def get_music21_objects_for_score(classinfo, ascore:Score, partnames:[str]=None, partnumbers:[int]=None) ->  (pd.DataFrame,{str},{int}):
        if classinfo is note.Note:
            return MusicUtils.get_notes_for_score(ascore, partnames, partnumbers)
        elif classinfo is interval.Interval:
            return MusicUtils.get_intervals_for_score(ascore, partnames, partnumbers)
        else:
            raise TypeError
    
    @staticmethod
    def get_intervals_for_score(ascore:Score, partnames:[str]=None, partnumbers:[int]=None) ->  (pd.DataFrame,{str},{int}):
        """Get the intervals of specified Parts of a Score as a pandas.DataFrame
        Arguments:
            ascore - a Score instance
            partnames - a list of part names to extract from Score. If None then intervals from all parts are extracted.
        
        DataFrame columns returned:
            interval  (interval.Interval)
            part_name
            part_number
            note1  (note.Note the first Note in the interval pair)
            note2  (note.Note the second Note in the interval pair)
            name (interval name as in "P5")
            directedName  (as in "P-5" for down a 5th)
            niceName
            semitones (int)
        
        Returns a 3-tuplet consisting of the intervals_df DataFrame,
        a [int] of part numbers, and a [str] of part names.
        """
        pdict = MusicUtils.get_score_intervals(ascore)
        intrvals_df = pd.DataFrame()
        part_number = 1
        df = None
        score_partnames = set()
        score_partnumbers = set()
        if partnames is None:
            partnames = list(pdict.keys())
        have_partnames = not ( partnames is None or len(partnames)==0)
        have_partnumbers = not (partnumbers is None or len(partnumbers)==0 or part_number in partnumbers)
        for k in pdict.keys():  # part names
                
                if (have_partnames and k in partnames) or (have_partnumbers and part_number in partnumbers):
                    part_intervals = pdict[k]
                    intervals =  [x['interval'] for x in part_intervals]
                    df = pd.DataFrame(data=intervals, columns=['interval'])
                    df['part_number'] = part_number
                    df['part_name'] = k
                    df['note1'] = [x['note1'] for x in part_intervals]
                    df['note2'] = [x['note2'] for x in part_intervals]
                    score_partnames.add(k)
                    score_partnumbers.add(part_number)
                    intrvals_df = pd.concat([intrvals_df, df])
                    part_number = part_number + 1
        if df is not None:
            # else this score has none of the parts specified 
            intrvals_df['name'] = [x.name for x in intrvals_df['interval']]
            intrvals_df['directedName'] = [x.directedName for x in intrvals_df['interval']]
            intrvals_df['niceName'] = [x.niceName for x in intrvals_df['interval']]
            intrvals_df['semitones'] = [x.semitones for x in intrvals_df['interval']]
            intrvals_df.reset_index(drop=True, inplace=True)       # make sure index is unique
        return intrvals_df, score_partnames, score_partnumbers
    

    @staticmethod
    def get_notes_for_score(ascore:Score, partnames:[str]=None, partnumbers:[int]=None) ->  (pd.DataFrame,{str},{int}):
        """Get the Notes of specified Parts from a score as a pandas.DataFrame
        Arguments:
            ascore - a Score instance
            partnames - a list of part names to extract from Score. If None, no parts are extracted.
                        If ['*'] (the default), then notes from all parts are extracted.
                                
        DataFrame columns returned:
            note (music21.note.Note)
            part_number
            part_name
            name  (just the pitch name as in "D")
            nameWithOctave   (pitch name with the octave as in "D5")
            pitch (music21.pitch.Pitch)
            pitchClass (integer)
            ps (pitch space - float)
            duration (music21.duration.Duration)
            type (the duration type string, for example "quarter")
            ordinal
            quarterLength (duration.quarterLength, float)
            quarterLengthNoTuplets
            scaleDegree (the ordinal of the pitch relative to the part's Key/KeySignature)
            
        Returns a 3-tuple consisting of the notes_df DataFrame,
        an integer set of part numbers, and a set(str) of part names.
        """
        pdict = MusicUtils.get_score_notes(ascore)    # {partname1 : [note.Note], partname2 : [note.Note], ... }
        score_parts = MusicUtils.get_score_parts(ascore)
        notes_df = pd.DataFrame()
        scale_degrees = []
        df = None
        part_number = 1
        score_partnames = set()
        score_partnumbers = set()
        if partnames is None:
            partnames = list(pdict.keys())
        have_partnames = not ( partnames is None or len(partnames)==0)
        have_partnumbers = not (partnumbers is None or len(partnumbers)==0 or part_number in partnumbers)
        for k in pdict.keys():
            if  (have_partnames and k in partnames) or (have_partnumbers and part_number in partnumbers):
                df = pd.DataFrame(data=pdict[k], columns=['note'])
                df['part_number'] = part_number
                df['part_name'] = k
                sdlist = MusicUtils.get_scale_degrees(score_parts[k])  # scale degrees for notes in this Part
                scale_degrees.extend([x['number'] for x in  sdlist])
                score_partnames.add(k)
                score_partnumbers.add(part_number)
                notes_df = pd.concat([notes_df, df])
                part_number = part_number + 1
                
        if df is not None:
            # else this score has none of the parts specified 
            dfnotes = notes_df['note']
            notes_df['name'] = [x.name for x in dfnotes]
            notes_df['nameWithOctave'] = [x.nameWithOctave for x in dfnotes]
            notes_df['pitch'] = [x.pitch for x in dfnotes]
            notes_df['pitchClass'] = [x.pitch.pitchClass for x in dfnotes]
            notes_df['ps'] = [x.pitch.ps for x in dfnotes]
            notes_df['duration'] = [x.duration for x in dfnotes]
            notes_df['type'] = [x.duration.type for x in dfnotes]
            notes_df['ordinal'] = [x.duration.ordinal for x in dfnotes]
            notes_df['quarterLength'] = [x.duration.quarterLength for x in dfnotes]
            notes_df['quarterLengthNoTuplets'] = [x.duration.quarterLengthNoTuplets for x in dfnotes]
            notes_df['scaleDegree'] = scale_degrees
            
            notes_df.reset_index(drop=True, inplace=True)       # make sure index is unique
        return notes_df, score_partnames, score_partnumbers
    
    @staticmethod
    def get_durations_from_notes(source_df:pd.DataFrame) -> pd.DataFrame:

        """Get the Durations from a notes or intervals DataFrame
        
        The notes_df argument has the columns described in get_notes_for_score().
        DataFrame columns returned:
            note (music21.note.Note)
            duration (music21.duration.Duration)
            type
            ordinal
            dots
            fullName
            quarterLength
            tuplets
        See the music21.duration documentation for details on individual fields
        """
        if 'duration' in source_df.columns:
            notes_df = source_df
            durations_df = pd.DataFrame(data=notes_df[['note','duration']], columns=['note','duration'])
            durations_df['type'] = [x.type for x in notes_df['duration']]
            durations_df['ordinal'] = [x.ordinal for x in notes_df['duration']]
            durations_df['dots'] = [x.dots for x in notes_df['duration']]
            durations_df['fullName'] = [x.fullName for x in notes_df['duration']]
            durations_df['quarterLength'] = [x.quarterLengthNoTuplets for x in notes_df['duration']]
            durations_df['tuplets'] = [x.tuplets for x in notes_df['duration']]
        else:
            intervals_df = source_df
            durations_df = pd.DataFrame(data=intervals_df[['note1']], columns=['note1'])
            durations_df['duration'] = [x.duration for x in intervals_df['note1']]
            durations_df['type'] = [x.duration.type for x in intervals_df['note1']]
            durations_df['ordinal'] = [x.duration.ordinal for x in intervals_df['note1']]
            durations_df['dots'] = [x.duration.dots for x in intervals_df['note1']]
            durations_df['fullName'] = [x.duration.fullName for x in intervals_df['note1']]
            durations_df['quarterLength'] = [x.duration.quarterLengthNoTuplets for x in intervals_df['note1']]
            durations_df['tuplets'] = [x.duration.tuplets for x in intervals_df['note1']]
            durations_df.rename(columns={'note1':'note'}, inplace=True)
        return durations_df
    
    @staticmethod
    def get_metadata_bundle(composer:str=None, title:str=None) -> metadata.bundles.MetadataBundle:
        """Gets a MetadataBundle for a composer and title.
            Arguments:
                composer - composer name, can be None
                title - a regular expression string used to do a title search.
                
            If title is just a string (no re characters) it will do an exact match.
            For example, to search for all Bach's works (in the corpus) that starts with "bwv1"
            specify get_metadata_bundle(composer='bach', title='^bwv1+')
        
        """
        meta = None
        if title is not None:
            titles_re = re.compile(title, re.IGNORECASE)
        if composer is not None:
            meta = corpus.search(composer,'composer')
            if title is not None:
                meta = meta.intersection(corpus.search(titles_re,'title'))
        elif title is not None:
            meta = corpus.search(titles_re,'title')
        return meta
    
    @staticmethod
    def get_all_score_music21_objects(classinfo, composer=None, title=None, partnames=None, partnumbers=None):
        if classinfo is note.Note:
            return MusicUtils.get_all_score_notes(composer, title, partnames, partnumbers)
        elif classinfo is interval.Interval:
            return MusicUtils.get_all_score_intervals(composer, title, partnames, partnumbers)
        else:
            raise TypeError

    @staticmethod
    def get_all_score_notes(composer=None, title=None, partnames=None, partnumbers=None):
        scores, titles = MusicUtils.get_scores_from_corpus(composer, title)
        notes_df = pd.DataFrame()
        all_score_partnames = set()
        all_score_partnumbers = set()
        for i in range(len(scores)):
            score = scores[i]
            df,pnames,pnums = MusicUtils.get_notes_for_score(score, partnames, partnumbers)
            df['title'] = titles[i]
            notes_df = pd.concat([notes_df, df], ignore_index=True)
            all_score_partnames = all_score_partnames.union(pnames)
            all_score_partnumbers = all_score_partnumbers.union(pnums)
        return notes_df, all_score_partnames, all_score_partnumbers
            
    @staticmethod
    def get_all_score_intervals(composer=None, title=None, partnames=None, partnumbers=None):
        meta = MusicUtils.get_metadata_bundle(composer, title)
        intrvals_df = pd.DataFrame()
        all_score_partnames = set()
        all_score_partnumbers = set()
        for i in range(len(meta)):
            md = meta[i].metadata
            if MusicUtils.verbose > 0:
                    print(f"working on {md.title}")
            score = corpus.parse(meta[i])
            df,pnames,pnums = MusicUtils.get_intervals_for_score(score, partnames, partnumbers)
            if len(df) > 0:
                df['title'] = md.title
                intrvals_df = pd.concat([intrvals_df, df], ignore_index=True)
                all_score_partnames = all_score_partnames.union(pnames)
                all_score_partnumbers = all_score_partnumbers.union(pnums)
        return intrvals_df, all_score_partnames, all_score_partnumbers
    
    @staticmethod
    def get_scores_from_corpus(composer=None, title=None, keypart:str=None, filters:dict=None):
        """Gets a list of Score objects from the corpus matching the composer and title provided.
        
        Args:
            composer = the name of the composer (as it appears in the corpus), for example 'bach'
            title = the title to search. This can be a regular expression, for example '^bwv31[0-3]', or a single work name as in 'bwv310'
            keypart - the name of the Part (if any) that determines the overall score Key.
            filters - a dictionary of filter values. Currently only filter is 'mode' which can be 'major' or 'minor'
        Returns:
            a 2-element tupple of the list of matching Score, and a list of corresponding str (titles)
            
        Note this uses MusicUtils.get_metadata_bundle which uses music21.corpus to do the search.
        Because the filter is at the Score level, the 'mode' filter (if present) is applied only when the keypart argument is not None.
        If mode filter and keypart are both provided, then the Key to all Parts is set to be the same as in keypart.
        """
        scores = []
        titles = []
        meta = MusicUtils.get_metadata_bundle(composer, title)
        for i in range(len(meta)):
            md = meta[i].metadata
            ascore = corpus.parse(meta[i])
            if filters is not None and 'mode' in filters and keypart is not None:     # check if the score matches the filter
                mode = filters['mode']
                spinfo = MusicUtils.get_score_parts_info(ascore, partnames=[keypart])
                if spinfo[keypart]['mode']==mode:
                    #
                    # update the key to all parts
                    #
                    new_key = spinfo[keypart]['key']
                    for apart in ascore.parts:
                        if apart.partName != keypart:
                            measures = apart.getElementsByClass(Measure)
                            for m in measures:
                                keys = m.getElementsByClass([key.Key, key.KeySignature])
                                if len(keys) > 0:
                                    for k in keys:
                                        if MusicUtils.verbose > 0:
                                            print(f'update {m} in {md.title}  {apart.partName} to key:{new_key}')
                                        m.removeByClass([key.Key, key.KeySignature])
                                        m.insert(spinfo[keypart]['key'])
                    scores.append(ascore)
                    titles.append(md.title)
            else:   
                scores.append(ascore)
                titles.append(md.title)
                
        return scores,titles
    
    @staticmethod
    def show_measures(measures, how='text'):
        nmeasures = len(measures)
        print(f"number of measures: {nmeasures}")
        i = 1
        for measure in measures:
            notes = measure.getElementsByClass(['Note','Chord','Rest'])
            print('measure {}'.format(i))
            for n in notes:
                if n.isNote:
                    print(n.nameWithOctave)
                else:
                    print(n.fullName)
            i = i+1
            measure.show(how)   # if None, displays in MuseScore
    
    @staticmethod
    def show_intervals(df, what='name') -> str:
        int_string = ''
        for ki in df[what].values.tolist():
            int_string = int_string + str(ki) + ','
        return int_string.rstrip(',')
    
    @staticmethod
    def show_notes(df, what='name') -> str:
        """Creates a stringified list of notes from a DataFrame
            Args:
                df - the source DataFrame
                what - the DataFrame column to select ('name', 'nameWithOctave' or 'scaleDegree')
            For example, show_notes(notes_df, 'nameWithOctave'), len(notes_df)==2, would return
            a string like 'F#4,C#5'
        
        """
        notes_str = ''
        for kn in df[what].values.tolist():
            notes_str = notes_str + kn + ','
        return (notes_str.rstrip(','))
    
    @staticmethod
    def show_durations(df, what='quarterLength') -> str:
        duration_string = ''
        for ds in df[what].values.tolist():
            duration_string = duration_string + str(ds) + ','
        return duration_string.rstrip(',')
    
    @staticmethod
    def to_string(alist:[int]) -> str:
        """Stringifies an integer list.
            For example [-2,3] --> "-2,3", because of str(alist) formatting
            str([-2,3]) --> "['2', '3']"
            
        """
        lstr = ''
        for x in alist:
            lstr = lstr + str(x) + ','
        return lstr.rstrip(',')

    @staticmethod
    def note_info(note):
        dur = note.duration
        if note.isRest:
            info = f'name: {note.name}, fullName: {note.fullName}, type: {dur.type}, dots: {dur.dots}, quarterLength: {dur.quarterLength}'
        else:
            info = f'{note.nameWithOctave}, type: {dur.type}, dots: {dur.dots}, fullName: {dur.fullName}, quarterLength: {dur.quarterLength}, tuplets: {dur.tuplets}'
        return info

    @staticmethod
    def duration_info(dur) -> duration.Duration:
        info = f'type: {dur.type}, ordinal: {dur.ordinal}, dots: {dur.dots}, fullName: {dur.fullName}, \
        quarterLength {dur.quarterLength}, quarterLengthNoTuplets {dur.quarterLengthNoTuplets}, tuplets: {dur.tuplets}'
        return info
    
    @staticmethod
    def get_interval_stats(ascore, partnames=None, partnumbers=None):
        int_df,pnames,pnums = MusicUtils.get_intervals_for_score(ascore, partnames, partnumbers)
        int_df = int_df.groupby(by=['semitones']).count()[['interval']]
        int_df.rename(columns={'interval':'count'}, inplace=True)
        int_df.reset_index(inplace=True)       
        return int_df.sort_values(by='count', ascending=False)

    @staticmethod
    def create_note(start_note:note.Note, 
                    anInterval:interval.Interval=None, semitones:int=None,
                    dur:duration.Duration=None, quarterLen:int=None) -> note.Note:
        """Creates a new Note a given interval away from a starting note
        
        Args:
            start_note (note.Note): the anchor Note
            interval (interval.Interval): a valid Interval or None. If None, semitones must be present.
            semitones (int): interval expressed as semitones
            duration (duration.Duration): duration to assign to the new Note
            quarterLength (int): duration to assign to the new Note expressed as quarterLength
        Returns:
            A new Note that is the specified interval away from the start_note.
        Notes:
            * duration or quarterLength may be specified, but not both.
            * if both duration and quarterLength are none, the duration of the new Note
              will be the same as the duration of start_note
        """
        new_note = copy.copy(start_note)    # shallow copy
        if anInterval is None and semitones is None:
            raise ValueError('interval and semitones cannot both be None')
        intval = anInterval
        if anInterval is None:
            intval = interval.Interval(semitones)
        new_note = new_note.transpose(intval)
        if dur is None and quarterLen is not None:
            new_note.quarterLength = quarterLen
        elif dur is not None:
            new_note.duration = dur
        return new_note
    
    @staticmethod
    def random_notes(lower_ps:int, upper_ps:int, num:int=10, minval=0.5) -> [note.Note]:
        notes = []
        for n in range(num):
            ps = random.randrange(lower_ps,upper_ps)    # random pitch (ps values)
            dur = random.randrange(1, 8) * minval       # random durations as quarterLength
            notes.append(note.Note(ps=ps, quarterLength=dur))
        return notes
    
    @staticmethod
    def random_part(lower_ps:int, upper_ps:int, num:int=10, minval=0.5, 
                     clef=clef.TrebleClef(), instrument=instrument.Piano()):
        # minval is given as quarterLength, 0.5 is an eighth note, 0.25 is a 16th etc.
        part = Part()
        part.insert(0,instrument)
        notes = []
        notes.append(clef)
        for n in range(num):
            ps = random.randrange(lower_ps,upper_ps)    # random pitch (ps value) c4 to b6
            dur = random.randrange(1, 8) * minval    # random durations (multiples of 16th notes) as quarterLength
            notes.append(note.Note(ps=ps, quarterLength=dur))
        part.append(notes)
        return part
    
    @staticmethod
    def random_score(partnames:[str] = ['Soprano','Alto','Tenor','Bass'], length:int=20, min_duration:float=0.5, scale_name=None) -> Score:
        score_instruments = []
        score = Score()
        instruments_info = Instruments()
        instruments_pd = instruments_info.instruments_pd
        for pn in partnames:
            part_instrument = instruments_pd.loc[pn].instance
            score_instruments.append(part_instrument)
            pitch_range = instruments_pd.loc[pn]['range_ps']
            clef_name = instruments_pd.loc[pn]['clef']
            clef = instruments_info.clefs_pd.loc[clef_name]['instance']
            part = MusicUtils.random_part(pitch_range[0], pitch_range[1], length, min_duration, clef, instrument=part_instrument)
            score.append(part)
        return score
    
    @staticmethod
    def get_file_info(cpath:str, def_extension:str='mxl') -> dict:
        """Breaks up a path name into component parts
        
        """
        
        known_extensions = [def_extension, 'mxl','.xml','.musicxml','.json','.txt','.csv']
        x = cpath.split("/")
        paths = x[0:len(x)-1]
        filename = x[-1]
        ext = filename.split(".")
        name = ext[0]
        if len(ext)==2 and ext[1] in known_extensions:
            ext = ext[1]
            path = cpath      
        else:
            ext = def_extension
            filename = f"{filename}.{ext}"
            path = f"{cpath}.{ext}"
        p = pathlib.Path(path)
        exists = p.exists()
        return  {'paths':paths, 'path_text':path, 'filename':filename, 'name':name,'extension': ext, 'Path':p, 'exists':exists}

    @staticmethod
    def round_values(x, places=5):
        if not type(x) is str:
            return round(x, places)
        else:
            return x
    
    @staticmethod
    def get_timedelta(start_date=date(1970,1,1), end_date=date.today()) -> int:
        """Gets the number of elapsed seconds between two dates.
        
        Args:
            start_date (datetime.date): the starting date. Default value is Jan 1,1970
            end_date: the ending date. Default value is today()
        Returns:
            The absolute value of the number of elapsed seconds between the two dates.
        Notes:
            Useful in setting a random seed.
        
        """
        
        delta = end_date - start_date
        return abs(int(delta.total_seconds()))
    
    @staticmethod
    def get_score_parts(aScore:Score):
        """Get the Parts of a Score
        Args:
            aScore - a stream.Score instance
        Returns:
            A dict of stream.Part with the key partName
        
        """
        parts_dict = dict()
        if aScore is not None:
            parts = aScore.getElementsByClass(Part)
            for p in parts:
                parts_dict[p.partName] = p
        return parts_dict
    
    @staticmethod
    def get_keySignatures(apart:Part, default_keySignature:key.KeySignature=None):
        """Gets the KeySignatures appearing in a given Part
        
            Args:
                apart : a stream.Part instance
                default_keySignature : use this if not None for all KeySignatures/Keys
            Returns:
                a tupple consisting of 2 lists:
                [KeySignature] in the order of appearance
                [int] of measure numbers where the KeySignature starts
        """
        measures = apart.getElementsByClass(Measure)
        key_sigs = []
        measure_numbers = []
        for m in measures:
            keys = m.getElementsByClass([key.Key,key.KeySignature])
            for k in keys:
                if k is not None:
                    if default_keySignature is not None:
                        key_sigs.append(default_keySignature)
                    else:
                        key_sigs.append(k)
                    measure_numbers.append(m.measureNumber)
        return key_sigs,measure_numbers
    
    @staticmethod
    def get_score_keySignatures(ascore:Score) -> {str:tuple}:
        """Gets the KeySignatures of all parts of a Score
            Args:
                ascore - a Score instance
            Returns:
                a dictionary of tupple, where the key is the part name and the tuple is ([KeySignature], [measures])
        """
        parts = ascore.getElementsByClass(Part)
        pdict = dict()
        for apart in parts:
            pdict[apart.partName] = MusicUtils.get_keySignatures(apart)
        return pdict

    @staticmethod
    def adjust_accidental(aNote:note.Note, preference:object=default_pitch_map, inPlace=True) -> note.Note:
        adjusted_note = aNote
        if not inPlace:
            adjusted_note = copy.deepcopy(aNote)
        if isinstance(preference, dict):
            keys = preference.keys()

        p = adjusted_note.pitch.simplifyEnharmonic()
        if p.accidental is None:
            accidental = 'natural'
        else:
            accidental = p.accidental.name
        if isinstance(preference, dict):
            if p.name in keys:
                p = p.getEnharmonic()
        elif preference=='sharp' and 'flat' in accidental:
                p = p.getEnharmonic()
        elif preference=='flat'  and 'sharp' in accidental:
                p = p.getEnharmonic()
        adjusted_note.pitch = p
        
        return adjusted_note
                
    @staticmethod
    def adjust_accidentals(apart: Part, preference:object=default_pitch_map, inPlace=True) -> Part:
        """Adjusts the accidentals on all notes in a given Part.
            Arguments:
                apart - a music21.stream.Part instance which can be the entire part, or measures()
                preference - "sharp", "flat" or dict() of pitch mappings. Default is default_pitch_map:
                             {'Db':'C#', "D-":'C#', 'D#':'Eb', 'Gb':'F#', 'G-':'F#', 'Ab':'G#', 'A-':'G#', 'A#':'Bb' }
                inPlace - if True changes are applied to the Part argument
            Returns:
                The adjusted Part
        """
        adjusted_part = apart
        if not inPlace:
            adjusted_part = copy.deepcopy(apart)
        part_notes = MusicUtils.get_part_notes(adjusted_part)

        for aNote in part_notes:
            aNote = MusicUtils.adjust_accidental(aNote, preference, inPlace=True)
        return adjusted_part

    @staticmethod
    def adjust_score_accidentals(ascore:Score, preference:object=default_pitch_map, partnames:[str]=None, inPlace=True) -> Score:
        """Adjusts the accidentals on all notes in a given score for specified part names
        
        """
        parts = ascore.getElementsByClass(Part)
        new_score = Score()
        for apart in parts:
            pname = apart.partName
            if partnames is None or pname in partnames:
                tp = MusicUtils.adjust_accidentals(apart, preference, inPlace)
                new_score.append(tp)
        return new_score
    
    @staticmethod
    def get_transposition_intervals(keys:[key.Key], key2:key.Key=C_Major, key2_minor:key.Key=A_Minor) -> [interval.Interval]:
        intval = []
        p2 = None
        for akey in keys:
            k = akey
            if not isinstance(akey, key.Key):
                k = akey.asKey()
            p1 = k.getPitches()[0]
            if k.mode == 'major':
                p2 = key2.getPitches()[0]
            else:
                p2 = key2_minor.getPitches()[0]
                
            interval_p1p2 = interval.Interval(noteStart = p1,noteEnd = p2)
            if abs(interval_p1p2.semitones) > 6:
                interval_p1p2 = interval_p1p2.complement
            if MusicUtils.verbose > 1:
                print('transposition key pitches {}, {} intervals p1p2 {}'.format(p1.nameWithOctave,p2.nameWithOctave, interval_p1p2.semitones))
            intval.append(interval_p1p2)
        return intval
    
    @staticmethod
    def transpose_part(apart:Part, target_key=C_Major, target_key_minor=A_Minor, \
                       instruments:Instruments=None, inPlace=False, adjustAccidentals=True) -> Part:
        """Transpose the notes in a given Part
            Args:
                apart : a stream.Part instance
                target_key : the transposition Key. Default is C-Major if not specified
                target_key_minor : the transposition Key if original key is minor mode. Default is A-Minor if not specified
                instruments - music.Instruments instance, if not None Part ranges are enforced after the transposition
                inPlace - if True, transpose in place. Otherwise transpose a copy
                adjustAccidentals - if True (the default) adjust all accidentals according to the caller's preference
            Returns:
                A Part with the notes transposed as specified.
                The Part argument is not modified if inPlace is False.
        """
        key_sigs,measure_numbers = MusicUtils.get_keySignatures(apart)
        measure_numbers.append(len(apart))
        transposition_intervals = MusicUtils.get_transposition_intervals(key_sigs, key2=target_key, key2_minor=target_key_minor)
        transposed_part = apart
        if not inPlace:     # transpose a copy of the Part
            transposed_part = copy.deepcopy(apart)
            
        for i in range(len(transposition_intervals)):
            #
            # no need to transpose if the measures are already in the target_key
            # but still need to adjust accidentals
            #
            intval = transposition_intervals[i]
            if MusicUtils.verbose > 1:
                print(f"transposition interval: {intval}")
            part_measures = transposed_part.measures(measure_numbers[i], measure_numbers[i+1]-1)
            if intval.semitones != 0:
                part_measures.transpose(intval, inPlace=True)
            if adjustAccidentals:
                MusicUtils.adjust_accidentals(part_measures)   # use defaults for preference and inPlace (True)
        
        if instruments is not None:
            #
            # check if notes are in range for Instrument and adjust if necessary
            #
            for anote in transposed_part.flat.getElementsByClass('Note'):
                instruments.adjust_to_range(apart.partName, anote, inPlace=True)
        
        return transposed_part
    
    @staticmethod
    def transpose_score(ascore:Score, target_key=C_Major, target_key_minor=A_Minor, partnames:[str]=None, \
                        instruments:Instruments=None, inPlace=False, adjustAccidentals=True) -> Score:
        """Transpose an entire Score to a new Key
        
            Args:
                ascore - the Score to transpose
                target_key - the new Key, default is C-Major
                partnames - part names to include (and transpose)
                instruments - music.Instruments instance, if not None Part ranges are enforced after the transposition
                inplace - if True, transpose in place. Otherwise transpose a copy
            Returns:
                a transposed Score. The original is not modified if inPlace is False
        
        """
        parts = ascore.getElementsByClass(Part)
        new_score = Score()
        for p in parts:
            pname = p.partName
            if partnames is None or pname in partnames:
                if MusicUtils.verbose > 1:
                    print('transpose {}'.format(pname))
                tp = MusicUtils.transpose_part(p, target_key=target_key, target_key_minor=target_key_minor, \
                                               instruments=instruments, inPlace=inPlace, adjustAccidentals=adjustAccidentals)
                new_score.append(tp)
        return new_score
    
    @staticmethod
    def extend_parts(ascore:Score, padlen:duration.Duration, time_signature = None):
        '''
        Extend each Part in a Score to padlen (total duration in quarterLengths)
        by adding rests.
        '''
        measureLen = 4.0
        if time_signature is not None:
            measureLen = time_signature.numerator * time_signature.beatDuration.quarterLength
        
        parts = ascore.getElementsByClass(Part)
        for p in parts:
            plen = p.duration.quarterLength
            padding = math.ceil(padlen.quarterLength/measureLen) * measureLen - plen
            if MusicUtils.verbose > 0:
                print(f'{p.partName} duration: {plen}')
                print(f' extend {p.partName} by {padding} quarterLengths')
            if padding > 0:
                r = note.Rest()
                r.duration.quarterLength = padding
                p.append(r)


if __name__ == '__main__':
    print(MusicUtils.__doc__)
