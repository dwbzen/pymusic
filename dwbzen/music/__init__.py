from __future__ import absolute_import  # multi-line and relative/absolute imports

from .__version__ import __title__, __description__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__


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

from music.song import Song
from .keys import Keys
from .scale  import Scale
from .scales import Scales
from .chords import Chords
from .chord import Chord
from .musicCollector import MusicCollector
from .noteCollector import NoteCollector
from .intervalCollector import IntervalCollector
from .durationCollector import DurationCollector
from .intervalCollectorRunner import IntervalCollectorRunner
from .noteCollectorRunner import NoteCollectorRunner
from .musicProducer import MusicProducer
from .musicProducerRunner import MusicProducerRunner
from .musicUtils import MusicUtils
from .instruments import Instruments
from .musicScale import MusicScale
from .musicSubstitutionSystem import MusicSubstitutionSystem
from .musicSubstitutionRules import MusicSubstitutionRules
from .scoreGen import ScoreGen
from .scoreGenRunner import ScoreGenRunner
