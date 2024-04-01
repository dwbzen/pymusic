from __future__ import absolute_import  # multi-line and relative/absolute imports

from .__version__ import __title__, __description__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__

import sys
minPythonVersion = (3, 10)
minPythonVersionStr = '.'.join([str(x) for x in minPythonVersion])

del sys
del minPythonVersion
del minPythonVersionStr

__all__ = [
    'chord', 
    'chords', 
    'durationCollector', 
    'instruments', 
    'intervalCollector',
    'intervalCollectorRunner',
    'keys',
    'musicCollector',
    'musicProducer',
    'musicProducerRunner',
    'musicScale',
    'musicSubstitutionRules',
    'musicSubstitutionSystem',
    'musicUtils',
    'noteCollector',
    'noteCollectorRunner',
    'sample_usage',
    'scale',
    'scales',
    'scoreGen',
    'scoreGenRunner',
    'song'
]

from .chords import Chords
from .chord import Chord
from .durationCollector import DurationCollector
from .instruments import Instruments
from .intervalCollector import IntervalCollector
from .intervalCollectorRunner import IntervalCollectorRunner
from .keys import Keys
from .musicCollector import MusicCollector
from .musicProducer import MusicProducer
from .musicProducerRunner import MusicProducerRunner
from .musicScale import MusicScale
from .musicSubstitutionSystem import MusicSubstitutionSystem
from .musicSubstitutionRules import MusicSubstitutionRules
from .musicUtils import MusicUtils
from .noteCollector import NoteCollector
from .noteCollectorRunner import NoteCollectorRunner
from .sample_usage import keys_usage, scales_usage, song_usage
from .scale  import Scale
from .scales import Scales
from .scoreGen import ScoreGen
from .scoreGenRunner import ScoreGenRunner
from .song import Song


