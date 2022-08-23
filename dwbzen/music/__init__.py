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

from dwbzen.music.chords import Chords
from dwbzen.music.chord import Chord
from dwbzen.music.durationCollector import DurationCollector
from dwbzen.music.instruments import Instruments
from dwbzen.music.intervalCollector import IntervalCollector
from dwbzen.music.intervalCollectorRunner import IntervalCollectorRunner
from dwbzen.music.keys import Keys
from dwbzen.music.musicCollector import MusicCollector
from dwbzen.music.musicProducer import MusicProducer
from dwbzen.music.musicProducerRunner import MusicProducerRunner
from dwbzen.music.musicScale import MusicScale
from dwbzen.music.musicSubstitutionSystem import MusicSubstitutionSystem
from dwbzen.music.musicSubstitutionRules import MusicSubstitutionRules
from dwbzen.music.musicUtils import MusicUtils
from dwbzen.music.noteCollector import NoteCollector
from dwbzen.music.noteCollectorRunner import NoteCollectorRunner
from dwbzen.music.sample_usage import keys_usage, scales_usage, song_usage
from dwbzen.music.scale  import Scale
from dwbzen.music.scales import Scales
from dwbzen.music.scoreGen import ScoreGen
from dwbzen.music.scoreGenRunner import ScoreGenRunner
from dwbzen.music.song import Song


