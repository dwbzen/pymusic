'''
Created on Feb 22, 2021

@author: don_bacon
'''
import json
from music.keys import Keys
from music.song import Song
from music.scales import Scales

def keys_usage(keys_file):   
    with open(keys_file, "r") as read_file:
        raw_data = json.load(read_file)
    # print(raw_data)
    
    keys = Keys(raw_data)
    
    print('Key names: {}'.format(keys.key_names))
    print(keys.key['B-Major'])
    
def song_usage(song_file):
    with open(song_file, "r") as read_file:
        song_data = json.load(read_file)
    song = Song(song_data)
    df_notes = song.df_notes
    df_harmony = song.df_harmony
    
    # select notes for section = 'verse-1'
    df_verse1_notes = df_notes.loc[df_notes.loc[:, 'section'] == 'verse-1', :]
    print(df_verse1_notes.head())
    
    # select rows having specific chords
    print(df_harmony[df_harmony['chord'].isin(['Bb', 'F7'])])
    
def scales_usage(scales_file):
    _scales = Scales(json_file_name=scales_file)
    print("scales file: {}".format(_scales.scales_file))
    print("scale names: {}".format(_scales.scale_names))
    # select a specific scale
    print("Dorian b2: \n{}".format(_scales.scale['Dorian b2'].scale))
    # get the DataFrame
    scales_df = _scales.scales_df
    scales_df_blues = scales_df[scales_df['groups'].apply(lambda x:'blues' in x)]
    
    print('blues scales with 7 notes: \n{}'.format( scales_df_blues[scales_df_blues['size']==7][['name', 'formula_str']]))


if __name__ == '__main__':
    print('Sample usage of Keys and Song')
    keys_file = "../../resources/keys.json"
    song_file = "../../resources/songs/Penny Lane.json"
    scales_file = "../../resources/common_scaleFormulas.json"
    keys_usage(keys_file)
    song_usage(song_file)
    scales_usage(scales_file)

    
    