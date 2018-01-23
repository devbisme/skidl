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
Functions for finding/displaying parts.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
import os
import os.path

from .py_2_3 import *  # pylint: disable=wildcard-import
from .utilities import *


def search(term, tool=None):
    """
    Print a list of components with the regex term within their name, alias, description or keywords.
    """

    import skidl

    def search_libraries(term, tool):
        """Search for a regex term in part libraries."""

        parts = set(
        )  # Set of parts and their containing libraries found with the term.

        for lib_dir in skidl.lib_search_paths[tool]:
            print('lib_dir = {}'.format(lib_dir))
            # Get all the library files in the search path.
            try:
                lib_files = os.listdir(lib_dir)
            except (FileNotFoundError, OSError):
                logger.warning("Could not open directory '{}'".format(lib_dir))
                lib_files = list(
                )  # Empty list since library directory was not found.
            lib_files = [
                l for l in lib_files if l.endswith(lib_suffixes[tool])
            ]

            for lib_file in lib_files:
                print(
                    ' ' * 79, '\rSearching {} ...'.format(lib_file), end='\r')
                lib = skidl.SchLib(
                    os.path.join(lib_dir, lib_file),
                    tool=tool)  # Open the library file.

                def mk_list(l):
                    """Make a list out of whatever is given."""
                    if isinstance(l, (list, tuple)):
                        return l
                    if not l:
                        return []
                    return [l]

                # Search the current library for parts with the given term in
                # each of the these categories.
                for category in ['name', 'alias', 'description', 'keywords']:
                    for part in mk_list(lib.get_parts(**{category: term})):
                        part.parse(
                        )  # Parse the part to instantiate the complete object.
                        parts.add(
                            (lib_file,
                             part))  # Store the library name and part object.
                print(' ' * 79, end='\r')

        return list(
            parts)  # Return the list of parts and their containing libraries.

    if tool is None:
        tool = skidl.get_default_tool()

    term = '.*' + term + '.*'  # Use the given term as a substring.
    parts = search_libraries(term,
                             tool)  # Search for parts with that substring.

    # Print each part name sorted by the library where it was found.
    for lib_file, p in sorted(parts, key=lambda p: p[0]):
        print('{}: {} ({})'.format(lib_file, getattr(p, 'name', '???'),
                                   getattr(p, 'description', '???')))


def show(lib, part_name, tool=None):
    """
    Print the I/O pins for a given part in a library.

    Args:
        lib: Either a SchLib object or the name of a library.
        part_name: The name of the part in the library.
        tool: The ECAD tool format for the library.

    Returns:
        A Part object.
    """

    import skidl

    if tool is None:
        tool = skidl.get_default_tool()
    try:
        return skidl.Part(
            lib, re.escape(part_name), tool=tool, dest=skidl.TEMPLATE)
    except Exception:
        return None
