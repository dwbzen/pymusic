
from music21 import stream, interval, corpus, converter, note, duration
import music
import pandas as pd
import pathlib

class Utils(object):
    
    verbose = 0
    
    #
    # gets and returns an individual score
    #
    @staticmethod
    def get_score(self, file_path):
        score = None
        return score
    
    #
    # get intervals for a Part
    #
    @staticmethod
    def get_part_intervals(apart):
        intrvals = []
        part_notes = apart.flat.getElementsByClass('Note')
        for ind in range(len(part_notes)-1):
            n1 = part_notes[ind]
            n2 = part_notes[ind+1]
            i = interval.Interval(n1, n2)
            intrvals.append(i)
        return intrvals
    
    @staticmethod
    def get_part_notes(apart):
        part_notes = apart.flat.getElementsByClass('Note')
        return part_notes
    
    #
    # get the intervals for all Parts of a Score as a dict
    # key = partName
    # item = list of music21.interval.Interval
    #
    @staticmethod
    def get_score_intervals(ascore, partname=None) -> (stream.Score,str):
        parts = ascore.getElementsByClass(stream.Part)
        pdict = dict()
        for p in parts:
            pname = p.partName
            if partname is None or pname==partname:
                pdict[pname] = Utils.get_part_intervals(p)
        return pdict
    
    #
    # get the Notes for all Parts or the named part of a Score as a dict
    # Note - does not return Chord or Rest objects
    # key = partName
    # item = notes for that part as a list of music21.note.Note
    #
    @staticmethod
    def get_score_notes(ascore, partname=None) -> (stream.Score,str):
        parts = ascore.getElementsByClass(stream.Part)
        pdict = dict()
        for p in parts:
            pname = p.partName
            if partname is None or pname==partname:
                notes = Utils.get_part_notes(p)
                pdict[pname] = notes
        return pdict
    
    
    #
    # get the intervals of all Parts as a pandas.DataFrame with columns
    # interval (music21.interval.Interval)
    # name (string)
    # niceName (string)
    # semitones (int)
    #
    @staticmethod
    def get_intervals_for_score(ascore, partnames=None, partnumbers=None):
        pdict = Utils.get_score_intervals(ascore)
        intrvals_df = pd.DataFrame()
        part_number = 1
        for k in pdict.keys():  # part names
                if (partnames is None or k in partnames) or (partnumbers is None or part_number in partnumbers):
                    df = pd.DataFrame(data=pdict[k], columns=['interval'])
                    df['part_number'] = part_number
                    df['part_name'] = k
                    intrvals_df = intrvals_df.append(df)
                    part_number = part_number + 1
    
        intrvals_df['name'] = [x.name for x in intrvals_df['interval']]
        intrvals_df['directedName'] = [x.directedName for x in intrvals_df['interval']]
        intrvals_df['niceName'] = [x.niceName for x in intrvals_df['interval']]
        intrvals_df['semitones'] = [x.semitones for x in intrvals_df['interval']]
        return intrvals_df
    
    #
    # get the Notes of all Parts as a pandas.DataFrame with columns
    # Note (music21.note.Note)
    # name
    # nameWithOctave
    # pitch (music21.pitch.Pitch)
    # duration (music21.duration.Duration)
    # pitchClass (int)
    #
    @staticmethod
    def get_notes_for_score(ascore, partnames=None, partnumbers=None):
        pdict = Utils.get_score_notes(ascore)
        notes_df = pd.DataFrame()
        part_number = 1
        for k in pdict.keys():
            if (partnames is None or k in partnames) or (partnumbers is None or part_number in partnumbers):
                df = pd.DataFrame(data=pdict[k], columns=['note'])
                df['part_number'] = part_number
                df['part_name'] = k
                notes_df = notes_df.append(df)
                part_number = part_number + 1
        
        notes_df['name'] = [x.name for x in notes_df['note']]
        notes_df['nameWithOctave'] = [x.nameWithOctave for x in notes_df['note']]
        notes_df['pitch'] = [x.pitch for x in notes_df['note']]
        notes_df['duration'] = [x.duration for x in notes_df['note']]
        notes_df['pitchClass'] = [x.pitch.pitchClass for x in notes_df['note']]
        return notes_df
    
    @staticmethod
    def get_durations_from_notes(notes_df) -> pd.DataFrame:
        # 'type','ordinal','dots','full_name','quarterLength','tuplets'
        durations_df = pd.DataFrame(data=notes_df[['note','duration']], columns=['note','duration'])
        durations_df['type'] = [x.type for x in notes_df['duration']]
        durations_df['ordinal'] = [x.ordinal for x in notes_df['duration']]
        durations_df['dots'] = [x.dots for x in notes_df['duration']]
        durations_df['fullName'] = [x.fullName for x in notes_df['duration']]
        durations_df['quarterLength'] = [x.quarterLength for x in notes_df['duration']]
        durations_df['tuplets'] = [x.tuplets for x in notes_df['duration']]
        return durations_df
    
    @staticmethod
    def get_metadata_bundle(composer=None, title=None) -> (str,str):
        meta = None
        if composer is not None:
            meta = corpus.search(composer,'composer')
            if title is not None:
                meta = meta.intersection(corpus.search(title,'title'))
        elif title is not None:
            meta = corpus.search(title,'title')
        return meta
        
    @staticmethod
    def get_all_score_intervals(composer=None, title=None, partnames=None, partnumbers=None):
        meta = Utils.get_metadata_bundle(composer, title)
        intrvals_df = pd.DataFrame()
        for i in range(len(meta)):
            md = meta[i].metadata
            score = corpus.parse(meta[i])
            df = Utils.get_intervals_for_score(score, partnames, partnumbers)
            df['title'] = md.title
            intrvals_df = intrvals_df.append(df)
        return intrvals_df
    
    @staticmethod
    def get_all_score_notes(composer=None, title=None, partnames=None, partnumbers=None):
        meta = Utils.get_metadata_bundle(composer, title)
        notes_df = pd.DataFrame()
        for i in range(len(meta)):
            md = meta[i].metadata
            score = corpus.parse(meta[i])
            df = Utils.get_notes_for_score(score, partnames, partnumbers)
            df['title'] = md.title
            notes_df = notes_df.append(df)
        return notes_df
    
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
    def show_intervals(df, what='name') -> pd.DataFrame:
        int_string = str(df[what].values.tolist())
        return int_string
    
    @staticmethod
    def show_notes(df, what='name') -> pd.DataFrame:
        note_string = str(df[what].values.tolist())
        return note_string
    
    @staticmethod
    def show_durations(df, what='quarterLength'):
        duration_string = str(df[what].values.tolist())
        return duration_string
    
    @staticmethod
    def note_info(note):
        dur = note.duration
        if note.isRest:
            info = f'name: {note.name}, fullName: {note.fullName}, type: {dur.type}, dots: {dur.dots},\
            quarterLength: {dur.quarterLength}'
        else:
            info = f'{note.nameWithOctave}, type: {dur.type}, dots: {dur.dots},\
            fullName: {dur.fullName}, quarterLength: {dur.quarterLength}, tuplets: {dur.tuplets}'
        return info

    @staticmethod
    def duration_info(dur) -> duration.Duration:
        info = f'type: {dur.type}, ordinal: {dur.ordinal}, dots: {dur.dots}, fullName: {dur.fullName}, \
        quarterLength {dur.quarterLength}, tuplets: {dur.tuplets}'
        return info
    
    @staticmethod
    def get_interval_stats(ascore, partnames=None, partnumbers=None):
        int_df = Utils.get_intervals_for_score(ascore, partnames, partnumbers)
        int_df = int_df.groupby(by=['semitones']).count()[['interval']]
        int_df.rename(columns={'interval':'count'}, inplace=True)
        int_df.reset_index(inplace=True)       
        return int_df.sort_values(by='count', ascending=False)
    
    #
    # breaks up a path name into component parts
    #
    @staticmethod
    def get_file_info(cpath, def_extension='mxl'):
        known_extensions = [def_extension, 'mxl','.xml','.musicxml']
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
        return  {'paths':paths, 'path_text':path, 'filename':filename, 'name':name,'extension': ext, 'Path':p}

    @staticmethod
    def round_values(x, places=5):
        if not type(x) is str:
            return round(x, places)
        else:
            return x
    
    if __name__ == '__main__':
        print(Utils.__doc__)
