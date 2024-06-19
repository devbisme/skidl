# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handler for reading SKiDL libraries.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from builtins import str
import os.path

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass


from skidl.utilities import export_to_all



# These aren't used here, but they are used in modules
# that include this module.
lib_suffix = "_sklib.py"

__all__ = ["lib_suffix"]


@export_to_all
def default_lib_paths():
    """Return default list of directories to search for part libraries."""

    # Start search for part libraries in the current directory.
    paths = ["."]

    # Add the location of the default SKiDL part libraries.
    paths.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs"))

    return paths


@export_to_all
def get_fp_lib_tbl_dir():
    """Get the path to where the global fp-lib-table file is found."""

    return "" # No global fp-lib-table file for SKiDL.


@export_to_all
def load_sch_lib(self, filename=None, lib_search_paths_=None, lib_section=None):
    """
    Load the parts from a SKiDL schematic library file.

    Args:
        filename: The name of the SKiDL schematic library file.
    """

    from skidl import SchLib, SKIDL
    from skidl.tools import lib_suffixes
    from skidl.logger import active_logger
    from skidl.utilities import find_and_read_file

    try:
        contents, path = find_and_read_file(
            filename, lib_search_paths_, lib_suffixes[SKIDL]
        )
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
        exec(contents, vars_)  # Execute and store library in dict.

        # Now look through the dict to find the library object.
        for val in vars_.values():
            if isinstance(val, SchLib):
                # Overwrite self with the new library.
                self.__dict__.update(val.__dict__)
                return

        # Oops! No library object. Something went wrong.
        raise ValueError("No SchLib object found in {}".format(filename))

    except Exception as e:
        active_logger.error("Problem with {}".format(filename))
        active_logger.error(e)
        raise


@export_to_all
def parse_lib_part(self, partial_parse=False):  # pylint: disable=unused-argument
    """
    Create a Part using a part definition from a SKiDL library.
    """

    # Parts in a SKiDL library are already parsed and ready for use,
    # so just return the part.
    return self
