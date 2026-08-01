'''
Created on Jul 27, 2023

@author: don_bacon
'''

from game.gameObject import GameObject
from typing import Dict
import json

class Card(GameObject):
    """ Represents a single card in a standard poker deck, optionally including 2 Jokers """

    def __init__(self, name:str, value:int, number:int, suite:str=None, color:str=None):
        self._name = name
        self._suite = suite
        self._value = value
        self._color = color
        self._number = number
        self._card_dict:Dict = {number: {"name" : name, "value" : value}}

        if suite is not None:
            self._card_dict[number].update( {"suite" : suite} )
        if color is not None:
            self._card_dict[number].update( {"color" : color})
        
    @property
    def name(self)->str:
        return self._name
    
    @property
    def suite(self)->str:
        return self._suite
    
    @property
    def color(self)->str:
        return self._color
    
    @property
    def number(self)->int:
        return self._number
    
    @property
    def value(self):
        return self._value

    def to_dict(self)->dict:
        return self._card_dict
    
    def to_JSON(self) ->str:
        return json.dumps(self._card_dict)
    
    def __str__(self):
        return f"{self.name}" if self._suite is None else  f"{self.name} of {self.suite}" 
    
    