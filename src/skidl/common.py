# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Stuff everyone needs.
"""

import sys

try:
    import __builtin__ as builtins
except ModuleNotFoundError:
    import builtins


if sys.version_info.major == 2:
    # Python 2 doesn't have this exception, so spoof it.
    builtins.FileNotFoundError = OSError
else:
    # Python 3 doesn't have basestring,
    # Python 2 doesn't work with type(''),
    # so....
    builtins.basestring = type("")
