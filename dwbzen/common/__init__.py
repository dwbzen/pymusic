from __future__ import absolute_import  # multi-line and relative/absolute imports

from .__version__ import __title__, __description__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__

from .collector import Collector
from .characterCollector import CharacterCollector
from .characterCollectorRunner import CharacterCollectorRunner
from .markovChain import MarkovChain
from .producer import Producer
from .wordProducer import WordProducer
from .wordProducerRunner import WordProducerRunner
from .utils import Utils

