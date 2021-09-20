
from music21 import stream, interval, corpus
import pandas as pd

#
# get intervals for a Part
#
def get_part_intervals(apart):
    intrvals = []
    part_notes = apart.flat.getElementsByClass('Note')
    for ind in range(len(part_notes)-1):
        n1 = part_notes[ind]
        n2 = part_notes[ind+1]
        i = interval.Interval(n1, n2)
        intrvals.append(i)
    return intrvals

def get_part_notes(apart):
    part_notes = apart.flat.getElementsByClass('Note')
    return part_notes

#
# get the intervals for all Parts of a Score as a dict
# key = partName
# item = list of music21.interval.Interval
#
def get_score_intervals(ascore):
    parts = ascore.getElementsByClass(stream.Part)
    pdict = dict()
    for p in parts:
        pname = p.partName
        intrvals = get_part_intervals(p)
        pdict[pname] = intrvals
    return pdict

#
# get the Notes for all Parts of a Score as a dict
# Note - does not return Chord or Rest objects
# key = partName
# item = list of music21.note.Note
#
def get_score_notes(ascore):
    parts = ascore.getElementsByClass(stream.Part)
    pdict = dict()
    for p in parts:
        pname = p.partName
        notes = get_part_notes(p)
        pdict[pname] = notes
    return pdict


#
# get the intervals of all Parts as a pandas.DataFrame with columns
# interval (music21.interval.Interval)
# name (string)
# niceName (string)
# semitones (int)
#
def get_all_score_intervals(ascore):
    pdict = get_score_intervals(ascore)
    intrvals_df = pd.DataFrame()
    part_number = 1
    for k in pdict.keys():
            df = pd.DataFrame(data=pdict[k], columns=['interval'])
            df['part_number'] = part_number
            df['part_name'] = k
            intrvals_df = intrvals_df.append(df)
            part_number = part_number + 1

    intrvals_df['name'] = [x.name for x in intrvals_df['interval']]
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
def get_all_score_notes(ascore):
    pdict = get_score_notes(ascore)
    notes_df = pd.DataFrame()
    part_number = 1
    for k in pdict.keys():
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

def get_metadata_bundle(composer, title=None):
    meta = corpus.search(composer,'composer')
    if title is not None:
        meta = meta.intersection(corpus.search(title,'title'))
    return meta
    
def get_all_composer_score_intervals(composer, title=None):
    meta = get_metadata_bundle(composer, title)
    intrvals_df = pd.DataFrame()
    for i in range(len(meta)):
        md = meta[i].metadata
        score = corpus.parse(meta[i])
        df = get_all_score_intervals(score)
        df['title'] = md.title
        intrvals_df = intrvals_df.append(df)
    return intrvals_df

def show_measures(measures):
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
        measure.show('text')

if __name__ == '__main__':
    print('Sample music21 usage')
    sBach = corpus.parse('bwv67.4')
    soprano = sBach.parts[0]
    soprano_measures = soprano.getElementsByClass('Measure')
    show_measures(soprano_measures)

    
