'''
Created on Dec 1,, 2025

@author: don_bacon
'''

from datetime import datetime
from util.environment import Environment
from typing import Dict, List, Mapping
import argparse

"""
The format of each entry in a parts of speach file is
	<word><white space><POS tag(s)><newline>

	Where the POS tag is one or more of the following:
	N	Noun
	L   Proper noun (not tagged) - N and first letter upper case
	l   Improper noun (not tagged) - N, p and first letter lower case
	M   Male person first name
	F   Female person first name
	S   Surname (last names)
	p	Plural Noun
	h	Noun Phrase
	V	Verb (usually participle)
	t	Verb (transitive)
	i	Verb (intransitive)
	A	Adjective
	v	Adverb
	C	Conjunction
	P	Preposition
	!	Interjection
	r	Pronoun
	D	Definite Article
	I	Indefinite Article
	o	Nominative
	
	Derived Forms - derived from existing entries
	G   gerund (V or t + ing)
	Z   Adjectival verb (V or t + "er", as in taker, putter etc.)
	z   derived possessive noun (N or p + "er" )
	X	present tense verb (V, t)
	x	past tense verb (V, t)
	Additional - privately added POS files
	B	body part
	b	body part - male
	d	body part - female

  For example, the word abide can be a verb, transitive verb, or intransitive verb:
   abide	Vti
  
"""

class PartsOfSpeech(object):

    def __init__(self, pos_files:List[str]=None):
        pass

def main():
    parser = argparse.ArgumentParser(description="Load a part of speach file")

if __name__ == '__main__':
    main()
