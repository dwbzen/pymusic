# -*- coding: utf-8 -*- 
import pandas as pd
import string
import argparse
from markovify import split_into_sentences
from nltk.corpus import stopwords

class TextParser(object):
    
    _punct = None
    _sw = stopwords.words('english') # Show some stop words - common words

    def __init__(self, txt = None, source = None, maxlines=None, ignore_case=True, remove_stop_words=False):
        self._words = []
        self._lines = []
        self._sentences = []
        self._word_set = None
        self._nlines = 0
        self._word_counts = {}
        self._maxlines = maxlines
        self.words_df = None
        self.verbose = 0
        self.text = txt
        self._ignore_case = ignore_case    # if True convert all words to lower case
        self.source = source
        self._remove_stop_words = remove_stop_words
        if source is not None:
            fp = open(source, "r")
            self.text = fp.read()
            self.text = self.text.replace('\t',' ')
        if self.text is not None and len(self.text) > 0:
            self.parse_text(self.text, maxlines=maxlines)
    
    @staticmethod
    def remove_punctuation(txt):
        if TextParser._punct is None:
            TextParser._punct =  string.punctuation.replace("'", "")
            TextParser._punct = TextParser._punct.replace('-', '')
            u_punct = '\N{LEFT SINGLE QUOTATION MARK}\N{RIGHT SINGLE QUOTATION MARK}\N{LEFT DOUBLE QUOTATION MARK}\N{RIGHT DOUBLE QUOTATION MARK}'
            TextParser._punct = TextParser._punct + u_punct
            
        nopunc = [char for char in txt if char not in TextParser._punct]
        # Join the characters again to form the string.
        return ''.join(nopunc)
    
    def get_words(self):
        return self._words
    
    def get_lines(self):
        return self._lines
    
    def get_sentences(self):
        return self._sentences
    
    def size(self):
        return self._nlines
    
    def get_word_set(self):
        if self._word_set is None:
            self._set_word_set()
        return self._word_set
    
    def _set_word_set(self):
        self._word_set = set(self._words)
    
    def _set_word_counts(self, sort_counts=False, reverse=False):
        if len(self._word_counts) == 0:
            for w in self._word_set:
                self._word_counts |= {w:self._words.count(w)}
        if sort_counts:
            self._word_counts = dict(sorted(self._word_counts.items(), key=lambda item: item[1], reverse=reverse))
        self.words_df = pd.DataFrame(data=self._word_counts.items(), columns=['word','count'])
    
    def get_word_counts(self, sort_counts=False, reverse=False):
        if self._word_set is None:
            self.get_word_set()
        self._set_word_counts(sort_counts, reverse)
        return self._word_counts
    
    def parse_text(self, txt, maxlines=None):
        self.text = txt
        for l in txt.splitlines():
            if maxlines is not None and self._nlines >= maxlines:
                break
            if self.verbose > 0:
                print(f'line {self.nlines}: {l}')
            ls = split_into_sentences(l)
            for s in ls:
                self._sentences.append(s)
                s_rempunc = TextParser.remove_punctuation(s)
                words = s_rempunc.split(' ')
                if self._remove_stop_words:
                    self._words += [str.lower(w) for w in words if len(w) > 0 and w.lower() not in TextParser._sw ]
                else:
                    self._words += [str.lower(w) for w in words if len(w) > 0]
            self._lines.append(l)
            self._nlines += 1
        self._set_word_set()
        return self._nlines

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", help="in-line text input. One of --text or --source must be specified", default=None)
    parser.add_argument("-s", "--source", help="input file name")
    parser.add_argument("-v","--verbose", help="increase output verbosity", action="count", default=0)
    parser.add_argument("-i","--ignoreCase", help="ignore input case", action="store_true", default=False)
    parser.add_argument("-r", "--remove_stop_words", help="remove common stop words", action="store_true", default=False)
    parser.add_argument("-l", "--lines", help="Maximum number of lines to read. If not set, reads all source lines", type=int, default=None)
    args = parser.parse_args()
    text_parser = TextParser(txt=args.text, source=args.source, maxlines=args.lines, remove_stop_words=args.remove_stop_words)
    word_counts = text_parser.get_word_counts(sort_counts=True, reverse=True)
    words_df = text_parser.words_df
    #
    # display the top 20
    print(words_df.head(20))

