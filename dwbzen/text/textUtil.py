'''
Created on Jun 10, 2026

@author: don_bacon
'''

import argparse, json, random
from textwrap import dedent
from typing import List
from functools import reduce

def main():
    description = dedent("""
    Produce random samples of the letters of a given text string, optionally splitting by consonant-vowell.
    Output strings are in the same case as the input string unless --case ("u", "l") is specified.
    TODO JSON output
    """)
    parser = argparse.ArgumentParser(prog="TextUtil", description=description)
    parser.add_argument("sample_text")  # positional argument
    parser.add_argument("--split", "-s", help="Split resulting text as consonant-vowell",  action="store_true", default=False)
    parser.add_argument("--number", "-n", help="Number of samples to produce, default is 5", type=int, default=5)
    parser.add_argument("--format", "-f", help="Output format: list (the default), lines, json", type=str, choices=["list", "lines", "json"], default="list")
    parser.add_argument("--case", "-c", help="Convert output to the given case: u:upper, l:lower, oc:original case. Default is to keep original case.", 
                        type=str, choices=["u", "l", "oc"], default="oc")
    parser.add_argument("--sort", help="Sort output. Choices are asc(ending), desc(ending), none (the default)", 
                        type=str, choices=["asc", "desc", "none"], default="none")
    parser.add_argument("--dup", "-d", help="Eliminate duplicate letters in the output. Default is False", action="store_true", default=False)
    parser.add_argument("--sample", help="Create samples of the input of a specific length.", type=int, default=0)
    parser.add_argument("--group", "-g", type=str, default=None,
        help="""Group output lines by comma-separated lengths, for example: '--group 6,10'. 
 The sum of the group length must equal the number of characters in the input string.
 This option is incompatible with '--split.' and '--sample' """)
    
    args = parser.parse_args()
    input_len = len(args.sample_text)
    
    group_list = [] if args.group is None else [int(x) for x in args.group.split(",")] 
    if len(group_list) > 0:
        tl =  reduce(lambda x,y: x+y, group_list)
        if tl != input_len:
            errtxt = f'The sum of the group length: {tl} must equal the number of characters in the input string: {input_len}'
            raise RuntimeError(errtxt)
    if args.sample > 0:
        if args.sample > input_len:
            raise RuntimeError("Sample size cannot exceed the input string length")
        
    textUtil = TextUtil(args.sample_text, args.split, args.number, args.sort, group_list, args.sample, args.dup)
    result = textUtil.produce()
    if args.format=="list":
        print(result)
    elif args.format == "lines":
        for rtxt in result:
            txt = rtxt.upper() if args.case == "u" else rtxt.lower() if args.case == "l" else rtxt
            print(txt)
    else: # TODO json
        print(result)

class TextUtil(object):
    
    VOWELS = "aeiouAEIOU"
    
    def __init__(self, sample_text:str, split:bool, num:int, sort_order:str, group_list:List[int], sample_size:int=0, eliminate_dups:bool=False):
        """ Constructor """
        # print(f"args: sample: {sample_text}, split: {split}, number: {num}")
        sample = "".join(sorted(sample_text))
        self.sort_order = sort_order
        self.sample = "".join(set(sample)) if eliminate_dups else sample
        self.split = split
        self.number = num
        self.reverse_sort = (sort_order=="desc")
        self.group_list = group_list
        self.sample_size = sample_size
    
    def split_text(self, text, separator="-")->str:
        """Split a text string into consonant-vowell string separated by the character specified.
        """
        split_consonants = ""
        split_vowells = ""
        for c in text:
            if c in TextUtil.VOWELS:
                split_vowells+=c
            else:
                split_consonants+=c
        return f"{split_consonants}{separator}{split_vowells}" if len(split_vowells)>0 else  f"{split_consonants}"
    
    def produce(self)->List[str]:
        outlist = []
        sample_len = len(self.sample)
        for _ in range(self.number):
            txt = "".join(random.sample(self.sample, sample_len))
            if self.split:
                outlist.append(self.split_text(txt))
            elif self.sample_size > 0:
                txt = "".join(random.sample(self.sample, self.sample_size))
                outlist.append(txt)
            elif len(self.group_list) > 0:
                l = []
                start=0
                for elem in list(enumerate(self.group_list)):
                    l.append(txt[start:elem[1]+start])
                    start+=elem[1]
                outlist.append(" ".join(l))
            else:
                outlist.append(txt)
        #
        # sort the entire list if sort_order is specified
        #
        if self.sort_order != "none":
            outlist.sort(reverse=self.reverse_sort)
        return outlist

if __name__ == '__main__':
    main()
    