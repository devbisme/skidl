# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Handler for reading SKiDL libraries and generating netlists.
"""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)  # isort:skip

from builtins import str

from future import standard_library

from ...logger import logger

standard_library.install_aliases()


# These aren't used here, but they are used in modules
# that include this module.
tool_name = "skidl"
lib_suffix = "_sklib.py"


def load_sch_lib(self, filename=None, lib_search_paths_=None, lib_section=None):
    """
    Load the parts from a SKiDL schematic library file.

    Args:
        filename: The name of the SKiDL schematic library file.
    """

    from ...schlib import SchLib
    from ...skidl import lib_suffixes, logger
    from ...utilities import find_and_open_file
    from .. import SKIDL

    try:
        f, path = find_and_open_file(filename, lib_search_paths_, lib_suffixes[SKIDL])
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Unable to open SKiDL Schematic Library File {} ({})".format(
                filename, str(e)
            )
        )
    try:
        # The SKiDL library is stored as a Python module that's executed to
        # recreate the library object.
        vars_ = {
            "__file__": path,
        }
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


def parse_lib_part(self, get_name_only=False):  # pylint: disable=unused-argument
    """
    Create a Part using a part definition from a SKiDL library.
    """

    # Parts in a SKiDL library are already parsed and ready for use,
    # so just return the part.
    return self
