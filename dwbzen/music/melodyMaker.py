'''
Created on Nov 5, 2026

@author: don_bacon
'''

from music.keys import Keys
from music.key import  Key
from music.generalUtils import GeneralUtils
from music.musicUtils import MusicUtils
from music.melody import Melody
import argparse

class MelodyMaker(object):
    """
    """

    def __init__(self, params):
        """ Constructor """
        pass
    
def main():
    keys = Keys()
    key_names = keys.key_names
        
    description = "Construct and view a Melody"
    #
    # construction
    #
    parser = argparse.ArgumentParser(prog="Melody", description=description)
    parser.add_argument("--name", help="Melody name", type=str, default="MyMelody")
    parser.add_argument("--notes", help="String of comma-separated notes", type=str, default="C4/quarter")
    #
    # random melody arguments
    #
    parser.add_argument("--random", "-R",
                        help="Create a random melody of a specified length from a given range of notes. Format is: 'start_note/end_note/length'",
                        type=str, default=None)
    parser.add_argument("--rest", help="Probability that a rest will appear in a random melody Default is 0.0 (no rests)",
                        type=float, default=0.0)
    parser.add_argument("--sample", "-S", help="How to sample notes: 'choices': sample with replacement, 'sample': without replacement ", type=str,
                        choices=["sample","choices"], default="choices")
    parser.add_argument("--twelve_tone", help="Enable 12-tone melodies. Default is to sample only notes within the specified key.", 
                        action="store_true",  default=False)
    #
    # format and playback
    #
    parser.add_argument("--instrument", help="The instrument name, default is 'Piano'", type=str, default="Piano")
    parser.add_argument("--key", "-K", 
            help="Optional key signature, for example 'Eb-Major', 'F-Minor'. Default key is 'C-Major'. Used to determine accidentals in the scale and the tonic/root note.",
            choices = key_names, type=str, default="C-Major")
    parser.add_argument("--fmt", "-F", help="Display the Melody in MuseScore, lilypond or as a list of pitches or notes",  
        type=str, choices=["pitches", "notes", "musicxml", "musicxml.png", "text", "midi", "lily", "lily.pdf"], default="notes")
    #
    # additional parts (TODO)
    #
    parser.add_argument("--harmonize", "-H", help="Harmonize the main melody with a second melody part", type=str, default=None)
    parser.add_argument("--chords", "-C", help="Add a second part consisting of chords.", type=str, default=None)
    
    args = parser.parse_args()
    key_name = args.key
    
    if args.random is not None:
        rand_args = args.random.split("/")
        if len(rand_args) != 3:
            print("Format is: 'start_note/end_note/length'")
            return
        
        start_note = MusicUtils.get_note(rand_args[0])
        end_note = MusicUtils.get_note(rand_args[1])
        length = int(rand_args[2])
        
        rest_probabilty=args.rest
        twelve_tone = args.twelve_tone
        melody = Melody(name=args.name,  key_name=key_name, randomMelody=(start_note, end_note, length, args.sample, twelve_tone, rest_probabilty))

        melody.show(fmt=args.fmt, instrument_name=args.instrument)
        
    else:
        melody = Melody(args.name)
        note_list = args.notes.split(",")
        for anote in note_list:
            melody.add_note(anote)
        
        melody.show(fmt=args.fmt, instrument_name=args.instrument)
        
if __name__ == '__main__':
    main()


        