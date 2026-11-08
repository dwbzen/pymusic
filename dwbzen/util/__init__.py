'''
Created on Sept 7, 2025

@author: don_bacon
'''

from __future__ import absolute_import  # multi-line and relative/absolute imports
from __future__ import annotations

import sys
minPythonVersion = (13, 14)
minPythonVersionStr = '.'.join([str(x) for x in minPythonVersion])

del sys
del minPythonVersion
del minPythonVersionStr

__author__ = "Donald Bacon"
__version__ = "1.0"

__all__ = [
    'words',
    'mysticSeer',
    'environment'
]

from .words import Words
from .environment import Environment
from .mysticSeer import MysticSeer
from .card import Card
from .cardDeck import CardDeck
from .flashCards import FlashCards
