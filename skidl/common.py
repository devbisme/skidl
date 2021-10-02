# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Stuff everyone needs.
"""

try:
    import __builtin__ as builtins
except ModuleNotFoundError:
    import builtins

import sys

USING_PYTHON2 = sys.version_info.major == 2
USING_PYTHON3 = not USING_PYTHON2

if USING_PYTHON2:
    # Python 2 doesn't have this exception, so spoof it.
    builtins.FileNotFoundError = OSError

if USING_PYTHON3:
    # Python 3 doesn't have basestring,
    # Python 2 doesn't work with type(''),
    # so....
    basestring = type("")
