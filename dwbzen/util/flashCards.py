'''
Created on Apr 21, 2026

@author: dwbze
'''

import argparse, json
from common import Environment
from datetime import datetime
import random
import string
from typing import List
from textwrap import dedent

class FlashCards(object):
    
    def __init__(self, cardfile:str, rules_file:str, category:str, def_first:bool, name:str, only:bool, show:bool, levels:str=None, verbose=False):
        self.cardfile = cardfile
        self.rules_file = rules_file
        self.category = category.lower()
        self.definition_first = def_first
        self.only = only
        self.name = name
        self.flash_cards = None
        self.env = Environment.get_environment()
        self.resource_folder = self.env.get_resource_folder()
        self.show = show
        fname = f'{self.resource_folder}/{cardfile}'
        rname = f'{self.resource_folder}/{rules_file}'
        
        with open(fname, "r") as fp:
            self.flash_cards = json.load(fp)
        if verbose:
            print(json.dumps(self.flash_cards, indent=2))
            
        card_levels = self.flash_cards["card_levels"]    # the available levels
        if levels is None:
            self.levels = card_levels
        else:
            _levels = sorted( [int(x) for x in levels.split(",")] )
            if only:
                self.levels = [_levels[-1]]
            elif len(levels) == 1:
                self.levels = [x for x in card_levels if x<=_levels[-1]]
        
        # create a random seed based on the user's name and current date/time
        letters = string.ascii_letters + string.digits + string.punctuation
        seed = sum([letters.find(self.name[x]) for x in range(len(self.name))])
        seed += int(datetime.strftime(datetime.now(),"%f"))    # microseconds
        random.seed(seed)
    
    def get_entries(self)->List[dict]:
        categories = self.flash_cards["categories"] if self.category.upper()=="ALL" else [self.category]
        all_categories = []
        for cat in categories:
            entries = []
            category_questions = self.flash_cards[cat]
            for entry in category_questions:
                if entry["level"] in self.levels:
                    entries.append(entry)
            all_categories.append( {cat:entries})
        return all_categories
    
    def run_quiz(self) ->(int,int):
        print("""After the prompt, enter the definition.
        If the definition is given, enter the word that defines it.
        Enter a '?' to get a hint: details and/or examples if they exist.
        Enter '??' to get the answer and move to the next question.
        To exit the quiz, enter 'exit' or 'end'. """)
        score = 0
        count = 0
        categories = self.flash_cards["categories"] if self.category.upper()=="ALL" else [self.category]
        
        if self.definition_first:
            question_key = "definition"
            answer_key = "name"
        else:
            question_key = "name"
            answer_key = "definition"
        for cat in categories:
            category_questions = self.flash_cards[cat]
            _questions = [x[question_key] for x in category_questions if x["level"] in self.levels]
            _answers = [x[answer_key] for x in category_questions if x["level"] in self.levels]
            
            size = len(_questions)
            fn_example = lambda x:x.get("example", "N/A")
            _examples = [fn_example(x) for x in category_questions if x["level"] in self.levels]
            
            fn_details = lambda x:x.get("details", "N/A")
            _details =  [fn_details(x) for x in category_questions if x["level"] in self.levels]
            
            question_number = 0
            while question_number<size:
                your_answer = input(f"{_questions[question_number]}:  ")
                if your_answer in ["end", "exit"]:
                    break
                elif your_answer == "??":
                    print(f'the answer is: {_answers[question_number]}')
                elif your_answer == "?" or your_answer == "help":
                    print(f' example: {_examples[question_number]}\n details: {_details[question_number]}')
                    question_number -= 1    # repeat the question
                elif your_answer == _answers[question_number]: 
                    score += 1
                elif your_answer in _answers[question_number]:
                    print(f"'{your_answer}' is close. The correct answer is '{_answers[question_number]}'")
                else: 
                    print(f"'{your_answer}' is incorrect. The correct answer is '{_answers[question_number]}'")
                count += 1
                question_number += 1
            
        return (score,count)
        

def main():
    description = dedent("""
    Present flash cards to a user and validate the response. Also keeps score.
    """)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--file", "-F", help="Flash card JSON file", type=str, default="music_terms.json")
    parser.add_argument("--rules", "-R", help="Rules JSON file", type=str, default="music_rules.json")
    parser.add_argument("--cat", "-C", help="Quiz category", type=str,  
            choices=["tempo", "dynamics",  "structure_form", "performing_instructions", "character_style", "signs", "modify_link_terms", "history", "all"], default="all")
    
    parser.add_argument("--definition", "-D", help="Definition first, user provides the term name", action="store_true", default=False)
    # levels is a comma-separated list of 1 or more levels to include in the quiz
    parser.add_argument("--levels", "-L", help="Definition level(s)", type=str, default=None)
    parser.add_argument("--name", "-N", help="Your name, default is 'User'", type=str, default="User")
    parser.add_argument("--only", help="Present cards only at the level specified (instead of including previous levels)",  action="store_true", default=False)
    parser.add_argument("--verbose", "-V", help="Verbose output",  action="store_true", default=False)
    parser.add_argument("--ui", help="User interface to use: text or gui", type=str, choices=["text", "gui"], default="text")    #TODO
    parser.add_argument("--show", "-S", help="Display all the entries of a given level(s) and category.", action="store_true", default=False)
    args = parser.parse_args()
    
    flashcards = FlashCards(args.file, args.rules, args.cat, args.definition, args.name, args.only, args.show, args.levels, verbose=args.verbose)
    if args.show:
        all_entries = flashcards.get_entries()
        for entry in all_entries:
            jstr = json.dumps(entry, indent=2)
            print(jstr)

    else:
        score = flashcards.run_quiz()
        num_correct = score[0]
        num_questions = score[1]
        pct = int(100* num_correct/num_questions)
        if pct >= 70:
            print(f"Congratulations {args.name}!, you passed with a score of {pct}%: {num_correct} correct out of {num_questions} questions")
        else:
            print(f"{args.name} failed with a score of {pct}%: {num_correct} correct out of {num_questions} questions. Try again!")

if __name__ == '__main__':
    main()
    