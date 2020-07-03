# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2018 by XESS Corp.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Handler for reading SKiDL libraries and generating netlists.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import str

from future import standard_library

from ..common import *
from ..defines import SKIDL
from ..logger import logger

standard_library.install_aliases()


tool_name = SKIDL
lib_suffix = "_sklib.py"


def _load_sch_lib_(self, filename=None, lib_search_paths_=None):
    """
    Load the parts from a SKiDL schematic library file.

    Args:
        filename: The name of the SKiDL schematic library file.
    """

    from ..skidl import lib_suffixes, logger
    from ..SchLib import SchLib
    from ..defines import SKIDL
    from ..utilities import find_and_open_file

    try:
        f, _ = find_and_open_file(filename, lib_search_paths_, lib_suffixes[SKIDL])
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Unable to open SKiDL Schematic Library File {} ({})".format(
                filename, str(e)
            )
        )
    try:
        # The SKiDL library is stored as a Python module that's executed to
        # recreate the library object.
        vars_ = {}  # Empty dictionary for storing library object.
        exec(f.read(), vars_)  # Execute and store library in dict.

        # Now look through the dict to find the library object.
        for val in vars_.values():
            if isinstance(val, SchLib):
                # Overwrite self with the new library.
                self.__dict__.update(val.__dict__)
                return

        # Oops! No library object. Something went wrong.
        raise ValueError("No SchLib object found in {}".format(filename))

    except Exception as e:
        logger.error("Problem with {}".format(f))
        logger.error(e)
        raise


def _parse_lib_part_(self, get_name_only=False):  # pylint: disable=unused-argument
    """
    Create a Part using a part definition from a SKiDL library.
    """

    # Parts in a SKiDL library are already parsed and ready for use,
    # so just return the part.
    return self
