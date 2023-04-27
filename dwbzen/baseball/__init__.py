from __future__ import absolute_import  # multi-line and relative/absolute imports

from .__version__ import __title__, __description__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__

__all__ = [
    'databank',
    'batting',
    'retrosheet',
    'pitching'
]

from .databank import BaseballDatabank
from .retrosheet import RetroSheet
from .batting import Batting
from .pitching import Pitching
