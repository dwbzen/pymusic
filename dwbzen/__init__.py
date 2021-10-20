from __future__ import absolute_import
import music

__author__ = "Donald Bacon"
__version__ = "0.1.0"


# this defines what  is loaded when importing __all__
# put these in alphabetical order FIRST dirs then modules
# but: base must come first; in some cases other modules depend on
# definitions in base


__all__ = [
    # sub folders
    'common',
    'music'
]

# -----------------------------------------------------------------------------
# this brings all of our own __all__ names into the dwbzen package namespace
# pylint: disable=wildcard-import
from dwbzen import *  # @UnresolvedImport  # noqa: E402,F403