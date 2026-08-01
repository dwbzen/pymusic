'''
Created on Sep 29, 2025

@author: don_bacon
'''

import argparse, json
from functools import reduce
from typing import List, Dict
from enum import StrEnum, auto
from textwrap import dedent
import re

class MatchType(StrEnum):
    NONE    = auto()    # "none"
    ONLY    = auto()
    ANY     = auto()
    DIST    = auto()
    ALL     = auto()

def read_words(wordfile, wordlen:range, letters:str, match_type:MatchType=None, letters_dist:dict=None, regex:re.Pattern=None)->tuple[int, List[str]]:
    """Read words of a given length and optionally include only specific letters
        Arguments:
            wordfile - words file for example: "C:/data/12dicts-6.0.2/American/2of12.txt"
            wordlen - range of lengths of the words to read
            letters - read those words whose characters are in this string
            match_type - mandatory if 'letters' is specified.
                         ANY to match any of the characters in letters (the default)
                         ONLY match words that contain only those characters in letters
                         ALL match words that contain all the characters in letters, but can contain other letters as well.
                         DIST match words that contain only those characters in letters in the same distribution
                         NONE if words must contain none the characters in letters
                         Note that using MatchType.NONE can produce lengthly results.
            letters_dist - letter distribution as a dict
            
        Returns a tuple (number of words read,  List of words read from the word file that meet the criteria)
    """
    words = []
    with open(wordfile, "r") as fp:
        for line in fp:
            line = line.strip("\n \t.;!?%")    # drop the trailing whitespace and punctuation
            if len(line) in wordlen:    # wordlen is a range object
                
                if letters_dist is not None and len(letters_dist)>0:
                    include = True
                    for c in set(line): # unique letters of line
                        count = line.count(c)
                        include = include and (count == letters_dist[c]) if c in letters_dist else False
                        if not include:
                            break
                        
                elif letters is not None:
                    # are the letters of the line in the letters argument?
                    _match_type = MatchType.ANY if match_type is None else match_type
                    result =  [x in letters for x in line]
                    match _match_type:
                        case MatchType.ONLY:
                            include = reduce(lambda x,y: x and y,result) 
                        case MatchType.ANY:
                            include = reduce(lambda x,y: x or y,result)
                        case MatchType.NONE:
                            include = reduce(lambda x,y: not (x or y),result)
                        case MatchType.ALL:
                            result = [x in line for x in letters]
                            include = reduce(lambda x,y: x and y,result)
                        case _:
                            include = True
                else:
                    include = True
                if include:
                    if regex is not None:
                        if regex.match(line) is not None:    # apply the match pattern
                            words.append(line)
                    else:
                        words.append(line)
    #print(f"{len(words)} words read")
    return (len(words),words)

class Words(object):
    """
    Encapsulate a word dictionary.
    Source dictionary format is each line corresponds to a single word or phrase.
    Any trailing newlines or punctuation is stripped.
    """

    WORDFILE = "/data/12dicts-6.0.2/American/2of12inf.txt"    # default word file path
    MAX_WORDLEN = 23

    def __init__(self, **kwargs):
        """ Constructor """
        wordfile = kwargs.get("wordfile", Words.WORDFILE)
        wordlen = kwargs.get("wordlen", range(1, Words.MAX_WORDLEN+1))
        letters = kwargs.get("letters", None)
        match_type = kwargs.get("match_type", None)
        letters_dist = kwargs.get("letters_dist", None)
        nwords = 0
        dict_words = []
        if (regex_str := kwargs.get("re", None)) is not None:
            try:
                regex = re.compile(regex_str)
                nwords, dict_words = read_words(wordfile=wordfile, wordlen=wordlen, letters=letters, match_type=match_type, letters_dist=letters_dist, regex=regex )
            except Exception as ex:
                print(f'"{regex_str}" is an invalid regular expression: {str(ex)}')
        else:
            nwords, dict_words = read_words(wordfile=wordfile, wordlen=wordlen, letters=letters, match_type=match_type, letters_dist=letters_dist, regex=None )
        
        self.size = nwords
        self.words = dict_words
    
    @staticmethod
    def parse_range(rangelen, word_len, input_len)->range:
        """Combine rangelen (which is a range string as in '2,5') and word_len (which is a single number)
            into a single range object.
            If both ranglen and word_len are provided and are valid, rangelen is used to produce the result
            and word_len is ignored. 
        """
        if rangelen is not None and len((r := rangelen.split(","))) >= 2:
            wordlen = range(int(r[0]), int(r[1])+1)
        elif word_len == 0:
            wordlen = range(input_len, input_len+1)
        else:
            wordlen = range(word_len, 1+word_len)
        return wordlen
    
    @staticmethod
    def get_letters_from_dist(dist:Dict(int,str))->(dict,str):
        letters_dist = {}
        letters = ""
        if dist is not None:
            ld = dist.split(",")    # list of char:number
            for d in ld:
                dist = d.split(":")
                letters_dist[dist[0]] = int(dist[1])
                letters += dist[0].lower()
        return (letters_dist,letters)

def main():
    description = dedent("""
    Read and optionally filter the contents of a dictionary file.
    A dictionary file is a text file comprised of a list of words and phrases, one per line.
    Leading and trailing white space and any special characters are filtered out prior to any matching.
    Running with no arguments will output the number of words read.
    To also display the words read, use --format (or -f) "text", "list" or "json"
    """)
    parser = argparse.ArgumentParser(prog="Words", description=description)
    parser.add_argument("--letters", "-L", help="Restrict to words containing these characters", type=str, default=None)
    parser.add_argument("--letters_dist", 
                        help="Letter distribution. Format is comma-separated list of 'letter':number. For example 'a':2 means matching words must have 2 letter a's.",
                        type=str, default=None)
    parser.add_argument("--match", "-m",
                        help="""How to match: 
                        all (words must contain all the letters), 
                        any (words must contain any of the letters, the default), 
                        only (match words containing only the given letters),
                        none (words that contain none of the given letters, or
                        dist (match words containing only the given letters and in the same distribution)""",
                        choices=["only", "any", "all", "dist", "none"], default="any")
    parser.add_argument("--re", help="Optional regular expression for word matching, applied on each line after the match result", type=str, default=None)
    parser.add_argument("--wordfile", "-d", help="Optional dictionary text filename/path", type=str, default=Words.WORDFILE)
    parser.add_argument("--len", "-l", help="Read words of this length only. Defaults to the input length.", type=int, default=0)
    parser.add_argument("--rangelen", "-R", 
                        help="Read words whose length is in the given range. Specify as comma delimited pair, as in '4,10'", 
                        type=str, default=None)
    parser.add_argument("--nwords", help="Read nwords number of words having the respective lengths given by --rangelen", type=int, default=1)    #TODO
    parser.add_argument("--format", "-f", help="Output format: text (the default) or json", type=str, 
                        choices=["text", "json", "list", "none"], default="none")
    parser.add_argument("--numbered", "-n", 
                        help="Number each output line. Applies to list and json formats only.", 
                        action="store_true", default=False)
    parser.add_argument("--verbose", "-v", help="Provide detailed result description.", action="store_true", default=False)
    args = parser.parse_args()
    
    match_type = MatchType[args.match.upper()]
    letters_dist,letters = Words.get_letters_from_dist(args.letters_dist)
    input_len = len(letters)
    wordlen = Words.parse_range(args.rangelen, args.len, input_len)    # result is a range object
    #
    # letters and letters_dist are mutually exclusive. 
    # if specified together, letters is ignored and letters_dist is used.
    # if letters_dist is specified, letters is created from that distribution keys.
    # if match type is 'dist' create a letters_dist from letters
    # 
    if args.letters_dist is None:
        _letters = args.letters.lower()
        letters = sorted(_letters)
        if match_type is MatchType.DIST:
            counts = [_letters.count(x) for x in _letters]
            letters_dist = dict(zip(_letters, counts, strict=True))
        
    _dict = Words(wordfile=args.wordfile, wordlen=wordlen, match_type=match_type, letters=letters, letters_dist=letters_dist, re=args.re) 
    description = f"words including {match_type.value.upper()} the letters '{letters}', length {wordlen.start} to {wordlen.stop-1}" if args.verbose else "words read"
    if args.format == "text":
        print(f"{_dict.size} {description}\n{_dict.words}")
    elif args.format == "json":
        if args.numbered:
            jstr = json.dumps({"size" : _dict.size, "words" : _dict.words}, indent=2)
        else:
            jstr = json.dumps({"size" : _dict.size, "words" : _dict.words})
        print(jstr)
    elif args.format == "list":
        if args.numbered:
            for i, word in enumerate(_dict.words):
                print(f"{i+1}\t{word}")
        else:
            for word in _dict.words: print(word)
    else:    # just print the #words read
        print(f"{_dict.size} words read")

if __name__ == '__main__':
    main()