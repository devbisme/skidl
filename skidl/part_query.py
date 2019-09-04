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
Functions for finding/displaying parts and footprints.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path
import re

from future import standard_library

from .py_2_3 import *  # pylint: disable=wildcard-import
from .utilities import *

standard_library.install_aliases()

# TODO: Use push-down automata to parse nested parenthetical expression
#       of AND/OR clauses for use in advanced part searching.
#       https://stackoverflow.com/questions/4284991/parsing-nested-parentheses-in-python-grab-content-by-level


def parse_search_terms(terms):
    """
    Return a regular expression for a sequence of search terms.

    Substitute a zero-width lookahead assertion (?= ) for each term. Thus,
    the "abc def" would become "(?=.*abc)(?=.*def)" and would match any string
    containing both "abc" and "def". Or "abc (def|ghi)" would become
    "(?=.*abc)((?=.*def)|(?=.*ghi))" and would match any string containing
    "abc" and "def" or "ghi". Quoted terms can be used for phrases containing
    whitespace.
    """
    return (
        re.sub(r"(([^()|\"\s]+)|(\".*?\"))\s*", r"(?=.*\1)", terms).replace('"', "")
        + ".*"
    )


def search_parts_iter(terms, tool=None):
    """Return a list of (lib, part) sequences that match a regex term."""

    import skidl
    from .SchLib import SchLib

    if tool is None:
        tool = skidl.get_default_tool()

    terms = parse_search_terms(terms)

    def mk_list(l):
        """Make a list out of whatever is given."""
        if isinstance(l, (list, tuple)):
            return l
        if not l:
            return []
        return [l]

    # Gather all the lib files from all the directories in the search paths.
    lib_files = list()
    for lib_dir in skidl.lib_search_paths[tool]:

        # Get all the library files in the search path.
        try:
            files = os.listdir(lib_dir)
        except (FileNotFoundError, OSError):
            logger.warning("Could not open directory '{}'".format(lib_dir))
            files = []

        files = [(lib_dir, l) for l in files if l.endswith(skidl.lib_suffixes[tool])]
        lib_files.extend(files)

    num_lib_files = len(lib_files)

    # Now search through the lib files for parts that match the search terms.
    for idx, (lib_dir, lib_file) in enumerate(lib_files):

        # If just entered a new lib file, yield the name of the file and
        # where it is within the total number of files to search.
        # (This is used for progress indicators.)
        yield "LIB", lib_file, idx + 1, num_lib_files

        # Parse the lib file to create a part library.
        lib = SchLib(
            os.path.join(lib_dir, lib_file), tool=tool
        )  # Open the library file.

        # Search the current library for parts with the given terms in
        # each of the these categories.
        for category in ["name", "aliases", "description", "keywords"]:
            for part in mk_list(
                # Get any matching parts from the library file.
                lib.get_parts(use_backup_lib=False, **{category: terms})
            ):
                # Parse the part to instantiate the complete object.
                part.parse(get_name_only=True)

                # Yield the part and its containing library.
                yield "PART", lib_file, part, part.name

                # Also return aliases.
                for alias in list(part.aliases):
                    yield "PART", lib_file, part, alias


def search_parts(terms, tool=None):
    """
    Print a list of parts with the regex terms within their name, alias, description or keywords.
    """

    parts = set()
    for part in search_parts_iter(terms, tool):
        if part[0] == "LIB":
            print(" " * 79, "\rSearching {} ...".format(part[1]), end="\r")
        elif part[0] == "PART":
            parts.add(part[1:4])
    print(" " * 79, end="\r")

    # Print each part name sorted by the library where it was found.
    for lib_file, part, part_name in sorted(list(parts), key=lambda p: p[0]):
        print(
            "{}: {} ({})".format(
                lib_file, part_name, getattr(part, "description", "???")
            )
        )


def show_part(lib, part_name, tool=None):
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
    from .Part import Part
    from .defines import TEMPLATE

    if tool is None:
        tool = skidl.get_default_tool()
    try:
        return Part(lib, re.escape(part_name), tool=tool, dest=TEMPLATE)
    except Exception:
        return None


# Cache for storing footprints read from .kicad_mod files.
footprint_cache = dict()


def search_footprints_iter(terms, tool=None, cache_invalid=True):
    """Return a list of (lib, footprint) sequences that match a regex term."""

    global footprint_cache

    import skidl

    if tool is None:
        tool = skidl.get_default_tool()

    terms = parse_search_terms(terms)

    # If the cache isn't valid, then make it valid by gathering all the
    # footprint files from all the directories in the search paths.
    if cache_invalid:
        footprint_cache = dict()
        for path in skidl.footprint_search_paths[tool]:
            for dir, subdirs, file_names in os.walk(path):

                # Don't visit hidden directories like .git.
                if os.path.basename(dir).startswith("."):
                    del subdirs[:]  # Don't visit any subdirs either.
                    continue

                # Skip directories without .pretty extension.
                if not dir.lower().endswith(".pretty"):
                    continue

                # Get name of library by stripping .pretty extension.
                lib_name = os.path.basename(dir)

                # Skip libraries having the same name that were already
                # handled in previous search path directories.
                if lib_name in footprint_cache:
                    continue

                # Create a dict containing the path to this library
                # and another dict for storing the contents of each
                # footprint file in the library.
                footprint_cache[lib_name] = {"path": dir, "modules": {}}

                # Create dict entries for the modules in the footprint lib directory.
                modules = footprint_cache[lib_name]["modules"]
                for file_name in file_names:
                    if file_name.lower().endswith(".kicad_mod"):
                        module_name = os.path.splitext(file_name)[0]
                        modules[module_name] = None  # Don't read file, yet.

    # Get the number of footprint libraries to be searched..
    num_fp_libs = len(footprint_cache)

    # Now search through the libraries for footprints that match the search terms.
    for idx, fp_lib in enumerate(footprint_cache):

        # If just entered a new library, yield the name of the lib and
        # where it is within the total number of libs to search.
        # (This is used for progress indicators.)
        yield "LIB", fp_lib, idx + 1, num_fp_libs

        # Get path to library directory and dict of footprint modules.
        path = footprint_cache[fp_lib]["path"]
        modules = footprint_cache[fp_lib]["modules"]

        # Search each module in the library.
        for module_name in modules:

            # If the cache isn't valid, then read each footprint file and store
            # it's contents in the cache.
            if cache_invalid:
                file = os.path.join(path, module_name + ".kicad_mod")
                with open(file, "r") as fp:
                    try:
                        # Remove any linefeeds that would interfere with fullmatch() later on.
                        modules[module_name] = [l.rstrip() for l in fp.readlines()]
                    except UnicodeDecodeError:
                        try:
                            modules[module_name] = [
                                l.decode("utf-8").rstrip() for l in fp.readlines()
                            ]
                        except AttributeError:
                            modules[module_name] = ""

            # Get the contents of the footprint file from the cache.
            module_text = tuple(modules[module_name])

            # Return a hit if the search terms matches the footprint name or
            # something in the footprint description or tag fields.

            if fullmatch(terms, module_name, flags=re.IGNORECASE):
                yield "MODULE", fp_lib, module_text, module_name
                continue

            for line in module_text:
                if ("(descr " in line or "(tags " in line) and fullmatch(
                    terms, line, flags=re.IGNORECASE
                ):
                    yield "MODULE", fp_lib, module_text, module_name
                    break


def search_footprints(terms, tool=None):
    """
    Print a list of footprints with the regex term within their description/tags.
    """

    footprints = []
    for fp in search_footprints_iter(terms, tool):
        if fp[0] == "LIB":
            print(" " * 79, "\rSearching {} ...".format(fp[1]), end="\r")
        elif fp[0] == "MODULE":
            footprints.append(fp[1:4])
    print(" " * 79, end="\r")

    # Print each module name sorted by the library where it was found.
    for lib_file, module_text, module_name in sorted(
        footprints, key=lambda f: (f[0], f[2])
    ):
        descr = "???"
        tags = "???"
        for line in module_text:
            try:
                descr = line.split("(descr ")[1].rsplit(")", 1)[0]
            except IndexError:
                pass
            try:
                tags = line.split("(tags ")[1].rsplit(")", 1)[0]
            except IndexError:
                pass
        print("{}: {} ({} - {})".format(lib_file, module_name, descr, tags))


def show_footprint(lib, module_name, tool=None):
    """
    Print the pads for a given module in a library.

    Args:
        lib: The name of a library.
        module_name: The name of the footprint in the library.
        tool: The ECAD tool format for the library.

    Returns:
        A Part object.
    """

    import skidl

    if tool is None:
        tool = skidl.get_default_tool()

    os.environ["KISYSMOD"] = os.pathsep.join(skidl.footprint_search_paths[tool])
    return pym.Module.from_library(lib, module_name)


# Define some shortcuts.
search = search_parts
show = show_part
