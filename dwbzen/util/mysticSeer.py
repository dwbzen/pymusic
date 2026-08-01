'''
Created on Oct 24, 2025

@author: don_bacon
'''

from datetime import datetime
from common import Environment
import argparse
import json
import random
import string
import tkinter as tk

class MysticSeer(object):
    """Ask a question - get an answer from the Mystic Seer. Adopted from the Twilight Zone episode, Nick of Time
    """

    def __init__(self, _name:str, quiet=False):
        """
        Constructor
        """
        self.name = _name.upper() if len(_name) > 0 else "NONE"
        self.quiet = quiet
        letters = string.ascii_letters + string.digits + string.punctuation
        seed = sum([letters.find(self.name[x]) for x in range(len(self.name))])
        seed += int(datetime.strftime(datetime.now(),"%f"))    # microseconds
        random.seed(seed)
        self.env = Environment.get_environment()
        self.resource_folder = self.env.get_resource_folder()
        # print(f"resource folder: {self.resource_folder}")
        fname = f'{self.resource_folder}/mysticSeer.json'
        with open(fname, "r") as fp:
            self.mystic_seer = json.load(fp)
        self.answers = self.mystic_seer["answers"]
        self.history = []
        
    def _get_selection(self)->dict:
        selection = random.choice(self.answers)
        return selection
        
    def ask_me(self)->str|None|list:
        prompt = "? " if self.quiet else "Ask your question (or type it in) and hit return. "
        question = input(prompt)
        if question in ["end","done","quit","exit"]:
            return None
        if question.startswith("hist"):
            return self.history
        selection = self._get_selection()
        answer = selection["answer"]
        #
        # don't choose the same answer twice in a row
        #
        histlen = len(self.history)
        if histlen == 0 or not answer == self.history[histlen-1]:
            self.history.append(answer)
        else:
            selection = self._get_selection()
            answer = selection["answer"]
            self.history.append(answer)
            
        choices = selection["choices"]
        #print(f"choices: {choices}")
        #print(f"answer: {answer}")
        if "$0" in answer:
            answer = answer.replace("$0", random.choice(choices[0]))
        if "$1" in answer:
            answer = answer.replace("$1", random.choice(choices[1]))
        return answer
    
    def help(self)->str:
        return self.mystic_seer["Help"]
    
    def mystic_seer_ui(self):
        pass

def main():
    parser = argparse.ArgumentParser(description="Ask a yes/no question - get an answer from the Mystic Seer. Inspired by the Twilight Zone episode, 'Nick of Time'")
    parser.add_argument("--quiet", "-q", help="Quiet prompt",  action="store_true", default=False)
    parser.add_argument("--ui", help="Use GUI interface. Default is text", type=str, choices=["text", "gui"], default="text" )
    args = parser.parse_args()
    if args.ui == "gui":
        pass
    
    name = input("What is your name? ")
    print(f"Thanks {name}. Ask the Mystic Seer a Yes/No question. You can type it in, or say it out loud.")
    mystic_seer = MysticSeer(name, args.quiet)
    if not args.quiet:
        print(mystic_seer.help())
    done = False
    while not done:
        answer = mystic_seer.ask_me()
        if answer is None:
            done = True
        else:
            print(answer)

if __name__ == '__main__':
    main()
    