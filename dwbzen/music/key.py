# ------------------------------------------------------------------------------
# Name:          key.py
# Purpose:       Encapsulate a music key.
#
# Authors:      Donald Bacon
#
# Copyright:    Copyright (c) 2026 Donald Bacon
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------


from typing import List
import music21

class Key(object):
    """Key represents a single Key as a dict with the Key name as the dictionary key.
        For example: { "name" : "G major",  "mode" : "Major", "accidental" : "sharps", "signature" : 1, "relativeKey" : "E-Minor"}
        Each entry is also represented as a property: key_name (for name), mode, accidental, signature, relativeKey, parallelKey
    """
    #
    # "sharp" and "flat" pitches include the accidental in order of appearance in circle of 5th keys:
    # "sharpNotes" and "flatNotes" do not.
    #
    KEY_SIGNATURES = {
        "sharp":  ["","F#","C#","G#","D#","A#","E#","B#"], "flat"  : ["","Bb","Eb","Ab","Db","Gb","Cb","Fb"],
        "sharpNotes": ["","F","C","G","D","A","E","B"], "flatNotes" : ["","B","E","A","D","G","C","F"]
    }
    
    def __init__(self, key_data:dict=None, name:str=None, mode:str=None, accidental:str=None, signature:int=0, relativeKey:str=None, parallelKey=None):
        if key_data is not None:
            self._key_data = key_data
        else:
            self._key_data = {"name" : name, "mode" : mode, "accidental" : accidental, "signature" : signature, "relativeKey" : relativeKey, "parallelKey" : parallelKey }
        
        self._key_name = key_data.get("name",None)
        assert(self._key_name is not None)
        self._name:str = self._key_name
        
        self._mode = self._key_data.get("mode","Major")
        self._accidental = self._key_data.get("accidental", "sharp")
        self._signature = self._key_data.get("signature",0)
        self._relativeKey = self._key_data.get("relativeKey", None)
        self._parallelKey = self._key_data.get("parallelKey", None)
        self.alternate_name = self._key_data.get("alternate_name",self._name)
        # assumes the name format is pitch-Major or pitch-Minor, as in "Bb-Minor"
        self._tonic = self._name[:self._name.index("-")]
    
    @property
    def key_name(self)->str:
        return self._key_name
    
    @property
    def mode(self)->str:
        return self._mode
    
    @property
    def accidental(self)->str:    # "sharp" or "flat"
        return self._accidental
    
    @property
    def signature(self)->int:
        return self._signature

    @property
    def relativeKey(self)->str:
        return self._relativeKey
    
    @property
    def parallelKey(self)->str:
        return self._parallelKey
    
    @property
    def tonic(self)->str:
        return self._tonic
    
    def get_key_signature(self, add_accidental:bool=True)->List[str]:
        """Returns the list of pitches that define this key. Returns an empty list for C-Major and A-Minor.
            Argument: add_accidental - if True then add the accidental (# or b) to the pitch. Default is True.
        """
        # self.accidental is "sharp" or "flat"
        accidentals = Key.KEY_SIGNATURES[self.accidental] if add_accidental else Key.KEY_SIGNATURES[f"{self.accidental}Notes"]
        num_accidentals = self.signature    # number of accidentals in the key signature: 0 through 7
        sig_pitches = accidentals[1:num_accidentals+1] if num_accidentals > 0 else []
        return sig_pitches
    
    @staticmethod
    def create_key(tonic:str, mode:str)->music21.key.Key:
        """ Create a music21.key.Key object 
            Arguments:
                tonic - the tonic note as a string. Upper case indicates Major, lower indicates Minor.
                    M or m may also be used. # indicates a sharp, a flat is "-" (minus)
                    Examples: 'C', 'b'
                mode - optional scale mode: ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian.
        """
        return music21.key.Key(tonic) if mode is None else music21.key.Key(tonic, mode.lower())
    
    @staticmethod
    def create_key_signature(signature:int)->music21.key.KeySignature:
        """ Create a music21 key.KeySignature given the signature.
            Argument: signature - the number of sharps (positive) or flats (negative).
                For example a signature of -3 is the key of Eb (or C-Minor)
        """
        assert(-7 <= signature <= 7)
        return music21.key.KeySignature(signature)
    
if __name__ == '__main__':
        k = Key(key_data={"name" : "Db-Major", "alternate_name" : "Db major",  "mode" : "Major", "accidental" : "flat", "signature" : 5, "relativeKey" : "Bb-Minor", "parallelKey" : "C#-Major"})
        print(f"{k.key_name}: mode: {k.mode}, signature: {k.get_key_signature()}")

    
