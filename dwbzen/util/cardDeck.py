'''
Created on Jul 27, 2023

@author: don_bacon
'''

import json, argparse
from util.card import Card
from typing import List
from textwrap import dedent
import random
import statistics

class CardDeck(object):
    """ Stardard deck of cards optionally including 2 Jokers.
        Need a standard deck for every 2 players, up to 8 players.
        So 3 decks required for up to 6 players, 4 decks for 8 players
        
    """

    SUITE_COLORS = { 'Hearts':'Red', 'Diamonds':'Red', 'Spades':'Black', 'Clubs':'Black' }
    NAME_VALUES = {"Joker":0, "Ace":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "Jack":10, "Queen":10, "King":10}


    def __init__(self, number_of_players:int=1, number_of_decks:int=1, include_jokers:bool=False):
        '''
        Constructor
        '''
        self._number_of_players = number_of_players
        self._number_of_decks = number_of_decks
        self._deck:List[Card] = list()
        self._has_jokers = include_jokers
        self._cards_index:List[int] = list()
        self._size = self.create_card_deck(number_of_decks=self._number_of_decks)
        self._cards_index = CardDeck.shuffle(self._size)
        self._next_index = 0
        self._last_index = self._size -1
        
    @property
    def deck(self) -> List[Card]:
        return self._deck
    
    @property
    def size(self)->int:
        return self._size
    
    @property
    def next_index(self):
        return self._next_index
    
    @property
    def last_index(self)->int:
        return self._last_index
    
    @next_index.setter
    def next_index(self, value):
        self._next_index = value
        
    @property
    def has_jokers(self)->bool:
        return self._has_jokers
        
    def create_card_deck(self, number_of_decks:int)->int:
        """Create a card deck comprised of a number of standard 52-card decks (54-cards if Jokers are included)
            Arguments:
                number_of_decks - number of standard card decks to combine. Default is 1
            Returns
                a count of the total number of cards
        """
        count = number_of_decks * (54 if self._has_jokers else 52)
        number = 0
        for _ in range(number_of_decks):
            for name in CardDeck.NAME_VALUES.keys():
                value = CardDeck.NAME_VALUES[name]
                
                if name == 'Joker' :
                    if self._has_jokers:
                        self._deck.append(Card(name, value, number)) # Jokers do not have a color or suite
                        number += 1
                        self._deck.append(Card(name, value, number)) # there are 2 Jokers per deck
                        number += 1
                else:
                    for suite in CardDeck.SUITE_COLORS.keys():
                        color = CardDeck.SUITE_COLORS[suite]
                        self._deck.append(Card(name, value, number, suite, color))
                        number += 1
        return count
    
    def peek(self, _index:int)->Card:
        """ Get the Card at a given index without advancing next_index
            Arguments: _index - desired index. No errors if index is out of bounds.
                If index is <0, the Card at index 0 is returned.
                If index > last_index, the Card at last_index is returned.
        """
        index = 0 if _index <0 else (self.last_index if _index > self.last_index else _index )
        card = self.deck[index]
        return card
    
    def to_dict(self)->dict:
        cards = [card.to_dict() for card in self.deck]
        #for card in self.deck:    # List[Card]
        #    cards.append(card.to_dict())
        cd = {"number_of_decks" : self._number_of_decks, "size" : self.size, "has_jokers" : self.has_jokers, "cards" : cards}
            
        return cd

    def to_JSON(self, indent=2)->str:
        return json.dumps(self.to_dict(), indent=indent)
        

    def draw(self) ->Card:
        """Draw a single card from the deck. If no cards remaining, re-shuffle and reset the next_index back to 0.
        """
        next_card = None
        if self.next_index < self.size:    # draw the next card
            nxt = self._cards_index[self.next_index]
            next_card = self._deck[nxt]
            self.next_index = self.next_index + 1
        else:
            self.next_index = 0
            CardDeck.shuffle(self._size)
            return self.draw()
        return next_card
    
    def draw_cards(self, ncards)->List[Card]:
        cards_list = [self.draw() for _ in range(ncards)]
        return cards_list
    
    def reshuffle(self)->None:
        """Reshuffles the deck and sets the next index to 0 """
        self._cards_index = CardDeck.shuffle(self._size)
        self._next_index = 0
    
    @staticmethod
    def shuffle(size:int) -> List[int]:
        return random.sample(list(range(0, size)), size)
    
    @staticmethod
    def simulate(_deck, trials:int, card_name:str)->str:
        """How many cards drawn on average until the specified card appears
        """
        deck:CardDeck = _deck
        if card_name in CardDeck.NAME_VALUES.keys():
            # 
            total_draws = []
            for _ in range(trials):
                ndraws = 1
                while(True):
                    card:Card = deck.draw()
                    if card.name == card_name:
                        total_draws.append(ndraws)
                        deck.reshuffle()
                        break
                    else:
                        ndraws += 1
            avg_draws = statistics.mean(total_draws)
            # print(total_draws)
            return f"Avg. number of draws: {avg_draws} to draw a {card_name}"
    
def main():
    description = dedent("""
    Create card deck(s) with or without Jokers. Optionally run a statistical simulation
    """)
    parser = argparse.ArgumentParser(prog="CardDeck", description=description)
    parser.add_argument("--jokers", "-j", help="Add Jokers to each deck", action="store_true", default=False)
    parser.add_argument("--decks", "-d", help="Number of decks. Default is 1.", type=int, default=1 )
    parser.add_argument("--players", "-p", help="Number of players. Default is 1.", type=int, default=1 )
    parser.add_argument("--card", "-c", help="Card to draw in simulated draws. Argument is the card name (Ace, King, 9, etc). Default is None",  
                        type=str,  default=None)
    parser.add_argument("--trials", "-t", help="Number of simulation trials to run. Default is 100.", type=int, default=100)
    parser.add_argument("--show", help="Show deck(s) and/or draws in JSON format. Default is none.", type=str, 
                        choices=["deck","draw", "both", "none"], default="none")
    
    args = parser.parse_args()
    
    card_deck = CardDeck(number_of_players=args.players, number_of_decks=args.decks, include_jokers=args.jokers)
    
    if args.show.startswith("deck") or args.show == "both":
        print(card_deck.to_JSON())
        
    if args.show.startswith("draw") or args.show == "both":
        for i in range(card_deck.size):
            card = card_deck.draw()
            print(f"{i+1}. {card}")
    
    if args.card is not None:
        result = CardDeck.simulate(card_deck, args.trials, args.card)
        print(result)

if __name__ == '__main__':
    main()
    
    