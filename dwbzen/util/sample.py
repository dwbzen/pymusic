'''
Created on Sep 27, 2025

@author: don_bacon
'''

import argparse, random, json
from functools import reduce
from typing import List
from util import Words


wordfile = "C:/data/12dicts-6.0.2/American/2of12.txt"

def main():
    parser = argparse.ArgumentParser(prog="Sample", description="Random sample text strings or read dictionary file")
    #
    # sample arguments
    #
    parser.add_argument("--text", "-t", help="sample source text")
    parser.add_argument("--check", "-c", help="Check if the random sample is a dictionary word", action="store_true", default=False)
    parser.add_argument("--match", "-m",
                        help="How to match: all (words must contain all the letters), any (words must contain any of the letters", \
                        choices=["all", "any"], default="any")
    parser.add_argument("--re", help="Optional regular expression for word matching. Overrides --match", type=str, default=None)
    parser.add_argument("--tries", help="If checking for dictionary words, number of sample tries", default=20)

    parser.add_argument("--letters", "-L", help="Restrict to words containing only these letters", type=str, default=None)
    parser.add_argument("--wordfile", "-d", help="Optional dictionary text filename/path", type=str, default=wordfile)
    parser.add_argument("--len", "-l", help="Read words of this length only, or 0 for all words", type=int, default=0)
    parser.add_argument("--rangelen", "-R", 
                        help="Read words whose length is in the given range. Specify as comma delimited duple, as in '4,10'", 
                        type=str, default=None)
    parser.add_argument("--slen", help="Length of sample words", type=int, default=0)
    parser.add_argument("--format", "-f", help="Output format: text or json", type=str, choices=["text", "json", "none"], default="text")
    args = parser.parse_args()
    
    slen = args.slen if args.slen > 0 else len(args.text)
    match_all = (args.match == "all")
    wordlen = Words.parse_range(args.rangelen, args.len)
    words = Words(wordfile=args.wordfile, wordlen=wordlen, match_all=match_all, letters=args.letters, re=args.re)
    samples = sample_text(args.text, words, slen, args.check, args.tries)
    print(samples)

def sample_text(sample_text:str, words:List[str], slen:int, check=False, tries=20):
    """Produce random samples of a given length from the provided sample text.
    """
    text = "".join(sorted(sample_text.lower()))
    #print(text)
    lst = []
    for _ in range(tries):
        theword = "".join(random.sample(text, k=slen))
        if not check or theword in words:
            if not theword in lst:
                lst.append(theword)
    return sorted(lst)

if __name__ == '__main__':
    main()