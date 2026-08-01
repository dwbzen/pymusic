'''
Created on Dec 1, 2025

@author: don_bacon
'''

from enum import Enum
from typing import Dict, List, Mapping
import json

class PartOfSpeech(Enum):
    NOUN = "N"
    PROPER_NOUN = "L"
    MALE_FIRST_NAME = "M"
    FEMALE_FIRST_NAME = "F"
    SURNAME = "S"
    IMPROPER_NOUN = "l"
    PLURAL_NOUN = "p"
    NOUN_PHRASE = "h"

    VERB = "V"
    VERB_TRANSITIVE = "t"
    VERB_INTRANSITIVE = "i"

    ADJECTIVE = "A"
    ADVERB = "v"
    CONJUNCTION = "C"
    PREPOSITION = "P"
    INTERJECTION = "!"
    PRONOUN = "r"
    ARTICLE_DEFINITE = "D"
    ARTICLE_INDEFINITE = "I"
    NOMINATIVE = "o"

    BODY_PART = "B"
    BODY_PART_MALE = "b"
    BODY_PART_FEMALE = "d"


