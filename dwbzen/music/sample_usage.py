'''
Created on Feb 22, 2021

@author: don_bacon
'''
import json
import music

def keys_usage(keys_file):   
    with open(keys_file, "r") as read_file:
        raw_data = json.load(read_file)
    # print(raw_data)
    
    keys = music.Keys(raw_data)
    
    print('Key names: {}'.format(keys.key_names))
    print(keys.key['B-Major'])
    
def song_usage(song_file):
    with open(song_file, "r") as read_file:
        song_data = json.load(read_file)
    song = music.Song(song_data)
    df_notes = song.df_notes
    df_harmony = song.df_harmony
    
    # select notes for section = 'verse-1'
    df_verse1_notes = df_notes.loc[df_notes.loc[:, 'section'] == 'verse-1', :]
    print(df_verse1_notes.head())
    
    # select rows having specific chords
    print(df_harmony[df_harmony['chord'].isin(['Bb', 'F7'])])
    
def scales_usage(scales_file):
    _scales = music.Scales(json_file_name=scales_file)
    print("scales file: {}".format(_scales.scales_file))
    print("scale names: {}".format(_scales.scale_names))
    # select a specific scale
    print("Dorian b2: {}".format(_scales.scale['Dorian b2'].scale))
    

if __name__ == '__main__':
    print('Sample usage of Keys and Song')
    keys_file = "../../resources/keys.json"
    song_file = "../../resources/songs/Penny Lane.json"
    scales_file = "../../resources/common_scaleFormulas.json"
    keys_usage(keys_file)
    song_usage(song_file)
    scales_usage(scales_file)

    
    