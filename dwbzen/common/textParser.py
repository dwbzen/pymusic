# -*- coding: utf-8 -*- 
import pandas as pd
import string
import argparse
from markovify import split_into_sentences
from nltk.corpus import stopwords
from nltk import word_tokenize

class TextParser(object):
    """TextParser is a general purpose text parsing class.
    
    In addition to parsing blocks of text, it also compiles word statistics.
    
    Dependencies: This uses NLTK corpus for stop words, and markovify for splitting lines into sentences.
        pip install nltk markovify pandas
        
    TODO Known issues:
        * support treating double quote and sentence terminators (.!?)  as a words instead of punctuation.
        * remove stop words from sentences if remove_stop_words is True. Implement a staticmethod for this.
        
    """
    _punct = None
    _sw = stopwords.words('english') # Show some stop words - common words
    _utf_punct = '\N{LEFT SINGLE QUOTATION MARK}\N{RIGHT SINGLE QUOTATION MARK}\N{LEFT DOUBLE QUOTATION MARK}\N{RIGHT DOUBLE QUOTATION MARK}'
    _utf_quotes = '\N{LEFT DOUBLE QUOTATION MARK}\N{RIGHT DOUBLE QUOTATION MARK}'
    _quotes = '"' + _utf_quotes

    def __init__(self, txt = None, source = None, maxlines=None, ignore_case=True, remove_stop_words=False):
        self._words = []        # words in order of appearance. Does not include stop words if remove_stop_words is True
        self._all_words = []    # words in order of appearance including stop words
        self._sentence_words = []    # words in sentence order with initial word of each sentence prefixed with a space
        self._lines = []
        self._sentences = []
        self._word_set = None
        self._nlines = 0
        self._word_counts = {}
        self._maxlines = maxlines
        self.counts_df = None
        self.verbose = 0
        self.text = txt
        self._ignore_case = ignore_case    # if True convert all words to lower case
        self.source = source
        self._remove_stop_words = remove_stop_words
        self.replace_utf_punctuation = True      # replace UTF-8 single, double quotation marks with ' and " respectively
        self.treat_dblquotes_as_words = True    # if true treat " as a word (instead of a quote)
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
            TextParser._punct = TextParser._punct + TextParser._utf_punct
            
        nopunc = [char for char in txt if char not in TextParser._punct]
        # Join the characters again to form the string.
        return ''.join(nopunc)
    
    @staticmethod
    def remove_quotes(txt):
        """Remove only the double quotes from a text string.
        
        This retains the final punctuation - period, ? or !
        """
        nopunc = [char for char in txt if char not in TextParser._quotes]
        # Join the characters again to form the string.
        return ''.join(nopunc)
    
    
    @staticmethod
    def replace_utf8_punctuation(txt):
        new_text = txt.replace('\N{LEFT DOUBLE QUOTATION MARK}', '"')
        new_text = new_text.replace('\N{RIGHT DOUBLE QUOTATION MARK}', '"')
        new_text = new_text.replace('\N{LEFT SINGLE QUOTATION MARK}', "'")
        new_text = new_text.replace('\N{RIGHT SINGLE QUOTATION MARK}', "'")
        return new_text
    
    @staticmethod
    def tokenize(self, txt) -> list:
        """Invokes NLTK word_tokenize function on a text string.
        
        Returns:
            a list of tokens which will include punctuation as individual list items
        
        """
        return word_tokenize(txt)
    
    def get_words(self):
        return self._words
    
    def get_all_words(self):
        return self._all_words
    
    def get_sentence_words(self):
        return self._sentence_words
    
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
        self.counts_df = pd.DataFrame(data=self._word_counts.items(), columns=['word','count'])
    
    def get_word_counts(self, sort_counts=False, reverse=False):
        if self._word_set is None:
            self.get_word_set()
        self._set_word_counts(sort_counts, reverse)
        return self._word_counts
    
    def parse_text(self, txt, maxlines=None):
        if self.replace_utf_punctuation:
            self.text = TextParser.replace_utf8_punctuation(txt)
        for l in self.text.splitlines():
            if maxlines is not None and self._nlines >= maxlines:
                break
            if self.verbose > 0:
                print(f'line {self.nlines}: {l}')
            ls = split_into_sentences(l)
            for s in ls:
                s_rempunc = TextParser.remove_punctuation(s)
                words = s_rempunc.split(' ')
                allwords = [str.lower(w) for w in words if len(w) > 0]
                self._all_words += allwords
                sentence_words = []
                if self._remove_stop_words:
                    if self._ignore_case:
                        sentence_words = [str.lower(w) for w in words if len(w) > 0 and w.lower() not in TextParser._sw ]
                    else:
                        sentence_words = [w for w in words if len(w) > 0 and w.lower() not in TextParser._sw ]
                else:
                    if self._ignore_case:
                        sentence_words = [str.lower(w) for w in words if len(w) > 0]
                    else:
                        sentence_words = [w for w in words if len(w) > 0]
                self._words += sentence_words
                
                if len(sentence_words) > 0:
                    sentence_words[0] = ' ' + sentence_words[0]
                    self._sentence_words += sentence_words
                    
                self._sentences.append(s)
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
    counts_df = text_parser.counts_df
    #
    # display the top 20
    print(counts_df.head(20))
    print(word_counts)
    
    sentences = text_parser.get_sentences()
    print(f'{len(sentences)} sentences\n ')
    #for s in sentences: print(s)
