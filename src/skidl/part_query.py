# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Functions for finding/displaying parts and footprints.

This module provides utilities to search for electronic parts and footprints
across libraries, and to display their details. It includes support for
regular expression searches and filtering on different properties.
"""

import os
import os.path
import re

from .logger import active_logger
from .utilities import export_to_all, fullmatch, rmv_quotes, to_list


__all__ = ["search", "show"]


# TODO: Use push-down automata to parse nested parenthetical expression
#       of AND/OR clauses for use in advanced part searching.
#       https://stackoverflow.com/questions/4284991/parsing-nested-parentheses-in-python-grab-content-by-level


def _parse_search_terms(terms):
    """
    Return a regular expression for a sequence of search terms.

    Converts a user-friendly search string into a regular expression pattern that can be
    used for matching part and footprint attributes. The function handles quoted phrases 
    and logical OR operations.

    Substitute a zero-width lookahead assertion (?= ) for each term. Thus,
    the "abc def" would become "(?=.*(abc))(?=.*(def))" and would match any string
    containing both "abc" and "def". Or "abc (def|ghi)" would become
    "(?=.*(abc))((?=.*(def|ghi))" and would match any string containing
    "abc" and "def" or "ghi". Quoted terms can be used for phrases containing
    whitespace.

    Args:
        terms (str): Space-separated search terms. Can include quoted phrases for exact matches
                    and '|' for OR operations.

    Returns:
        str: A regular expression pattern string that will match if all terms are found.

    Example:
        _parse_search_terms('resistor 10k') returns a regex that matches strings containing
        both 'resistor' and '10k'.
    """

    # Place the quote-delimited REs before the RE for sequences of
    # non-white chars to prevent the initial portion of a quoted string from being
    # gathered up as a non-white character sequence.
    terms = terms.strip().rstrip()  # Remove leading/trailing spaces.
    terms = re.sub(r"\s*\|\s*", r"|", terms)  # Remove spaces around OR operator.
    terms = re.sub(r"((\".*?\")|(\'.*?\')|(\S+))\s*", r"(?=.*(\1))", terms)
    terms = re.sub(r"[\'\"]", "", terms)  # Remove quotes.
    terms = terms + ".*"
    return terms


@export_to_all
def search_parts_iter(terms, tool=None):
    """
    Return an iterator of (lib, part) sequences that match regex terms.
    
    This generator function yields information about libraries being searched and parts
    found that match the search terms.
    
    Args:
        terms (str): Space-separated search terms to match against part attributes.
        tool (str, optional): The ECAD tool format for the libraries to search. 
                             Defaults to the currently configured tool.
    
    Yields:
        tuple: Either progress information as ("LIB", lib_file, index, total) 
               or part information as ("PART", lib_file, part_obj, part_alias).
    """

    import skidl
    import skidl.tools

    from .schlib import SchLib

    tool = tool or skidl.config.tool

    terms = _parse_search_terms(terms)

    def mk_list(l):
        """Make a list out of whatever is given."""
        if isinstance(l, (list, tuple)):
            return l
        if not l:
            return []
        return [l]

    # Gather all the lib files from all the directories in the search paths.
    lib_files = list()
    lib_suffixes = tuple(to_list(skidl.tools.lib_suffixes[tool]))
    for lib_dir in skidl.lib_search_paths[tool]:

        # Get all the library files in the search path.
        try:
            files = os.listdir(lib_dir)
        except (FileNotFoundError, OSError):
            active_logger.bare_warning(f"Could not open directory '{lib_dir}'")
            files = []

        files = [(lib_dir, l) for l in files if l.endswith(lib_suffixes)]
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

        # Search the current library for parts with the given terms.
        for part in mk_list(
            # Get any matching parts from the library file.
            lib.get_parts(use_backup_lib=False, search_text=terms)
        ):
            # Parse the part to instantiate the complete object.
            part.parse(partial_parse=True)

            # Return part name and aliases (everything is included in aliases).
            for alias in list(part.aliases):
                yield "PART", lib_file, part, alias


@export_to_all
def search_parts(terms, tool=None):
    """
    Print a list of parts with the regex terms within their name, alias, description or keywords.
    
    Searches through all available libraries for parts matching the given terms and prints
    the results to the console.
    
    Args:
        terms (str): Space-separated search terms to match against part attributes.
        tool (str, optional): The ECAD tool format for the libraries to search.
                             Defaults to the currently configured tool.
    
    Returns:
        None: Results are printed to the console.
    """

    parts = set()
    for part in search_parts_iter(terms, tool):
        if part[0] == "LIB":
            print(" " * 79, f"\rSearching {part[1]} ...", sep="", end="\r")
        elif part[0] == "PART":
            parts.add(part[1:4])
    print(" " * 79, end="\r")

    # Print each part name sorted by the library where it was found.
    for lib_file, part, part_name in sorted(list(parts), key=lambda p: p[0]):
        print(
            f"{lib_file}: {part_name} ({getattr(part, 'description', '???')})"
        )


@export_to_all
def show_part(lib, part_name, tool=None):
    """
    Print the I/O pins for a given part in a library.

    Creates a template Part object that can be inspected to see its pins and properties.

    Args:
        lib: Either a SchLib object or the name of a library.
        part_name (str): The name of the part in the library.
        tool (str, optional): The ECAD tool format for the library.
                             Defaults to the currently configured tool.

    Returns:
        Part: A template Part object if found, otherwise None.
    """

    import skidl

    from .part import TEMPLATE, Part

    tool = tool or skidl.config.tool

    try:
        return Part(lib, re.escape(part_name), tool=tool, dest=TEMPLATE)
    except Exception:
        return None


class FootprintCache(dict):
    """
    Dict for storing footprints from all directories.
    
    This cache stores footprint information from KiCad libraries to avoid
    repeatedly reading the same files from disk during searches.
    It maps library nicknames to a dict containing the path and module information.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the footprint cache.
        
        Args:
            *args, **kwargs: Arguments passed to the dict constructor.
        """
        super().__init__(*args, **kwargs)
        self.reset()  # Cache starts off empty, hence invalid.

    def reset(self):
        """
        Reset the footprint cache.
        
        Clears all cached footprint data and marks the cache as invalid.
        """
        self.clear()  # Clear out cache.
        self.valid = False  # Cache is empty, hence invalid.

    def load(self, path):
        """
        Load cache with footprints from libraries in fp-lib-table file.
        
        Reads the fp-lib-table file in the given path to identify and load
        footprint libraries into the cache.
        
        Args:
            path (str): Path to directory containing fp-lib-table file.
                       If no fp-lib-table is found, treats the path itself as a module library.
        """

        # Expand any env. vars and/or user in the path.
        path = os.path.expandvars(os.path.expanduser(path))

        # Read contents of footprint library file into a single string.
        try:
            # Look for fp-lib-table file and read its entries into a table of footprint module libs.
            with open(os.path.join(path, "fp-lib-table")) as fp:
                tbl = fp.read()
        except FileNotFoundError:
            # fp-lib-table file was not found, so create a table containing the path directory
            # as a single module lib.
            nickname, ext = os.path.splitext(os.path.basename(path))
            tbl = f'(fp_lib_table\n(lib (name {nickname})(type KiCad)(uri {path})(options "")(descr ""))\n)'

        # Get individual "(lib ...)" entries from the string.
        libs = re.findall(
            r"\(\s*lib\s* .*? \)\)", tbl, flags=re.IGNORECASE | re.VERBOSE | re.DOTALL
        )

        # Add the footprint modules found in each enabled KiCad library.
        for lib in libs:

            # Skip disabled libraries.
            disabled = re.findall(
                r"\(\s*disabled\s*\)", lib, flags=re.IGNORECASE | re.VERBOSE
            )
            if disabled:
                continue

            # Skip non-KiCad libraries (primarily git repos).
            type_ = re.findall(
                r'(?:\(\s*type\s*) ("[^"]*?"|[^)]*?) (?:\s*\))',
                lib,
                flags=re.IGNORECASE | re.VERBOSE,
            )[0]
            if type_.lower() != "kicad":
                continue

            # Get the library directory and nickname.
            uri = re.findall(
                r'(?:\(\s*uri\s*) ("[^"]*?"|[^)]*?) (?:\s*\))',
                lib,
                flags=re.IGNORECASE | re.VERBOSE,
            )[0]
            nickname = re.findall(
                r'(?:\(\s*name\s*) ("[^"]*?"|[^)]*?) (?:\s*\))',
                lib,
                flags=re.IGNORECASE | re.VERBOSE,
            )[0]

            # Remove any quotes around the URI or nickname.
            uri = rmv_quotes(uri)
            nickname = rmv_quotes(nickname)

            # Expand environment variables and ~ in the URI.
            uri = os.path.expandvars(os.path.expanduser(uri))

            # Look for unexpanded env vars and skip this loop iteration if found.
            def get_env_vars(s):
                """Return a list of environment variables found in a string."""
                env_vars = []
                for env_var_re in (r"\${([^}]*)}", r"\$(\w+)", r"%(\w+)%"):
                    env_vars.extend(re.findall(env_var_re, s))
                return env_vars

            unexpanded_vars = get_env_vars(uri)
            if unexpanded_vars:
                active_logger.bare_warning(
                    f"There are some undefined environment variables: {' '.join(unexpanded_vars)}"
                )
                continue

            # Get a list of all the footprint module files in the top-level of the library URI.
            try:
                filenames = [
                    fn
                    for fn in os.listdir(uri)
                    if os.path.isfile(os.path.join(uri, fn))
                    and fn.lower().endswith(".kicad_mod")
                ]
            except FileNotFoundError:
                active_logger.bare_warning(f"Library directory not found: {uri}")
                continue

            # Create an entry in the cache for this nickname. (This will overwrite
            # any previous nickname entry, so make sure to scan fp-lib-tables in order of
            # increasing priority.) Each entry contains the path to the directory containing
            # the footprint module and a dictionary of the modules keyed by the module name
            # with an associated value containing the module file contents (which starts off
            # as None).
            self[nickname] = {
                "path": uri,
                "modules": {os.path.splitext(fn)[0]: None for fn in filenames},
            }


# Cache for storing footprints read from .kicad_mod files.
footprint_cache = FootprintCache()


@export_to_all
def search_footprints_iter(terms, tool=None):
    """
    Return an iterator over footprints that match the regex terms.
    
    This generator function yields information about libraries being searched and footprints
    found that match the search terms.
    
    Args:
        terms (str): Space-separated search terms to match against footprint attributes.
        tool (str, optional): The ECAD tool format for the footprint libraries to search.
                             Defaults to the currently configured tool.
    
    Yields:
        tuple: Either progress information as ("LIB", lib_name, index, total) 
               or footprint information as ("MODULE", lib_name, module_text, module_name).
    """

    import skidl

    tool = tool or skidl.config.tool

    terms = _parse_search_terms(terms)

    # If the cache isn't valid, then make it valid by gathering all the
    # footprint files from all the directories in the search paths.
    if not footprint_cache.valid:
        footprint_cache.clear()
        footprint_cache.load(skidl.footprint_search_paths[tool])

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
            if not footprint_cache.valid:
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

            # Count the pads so it can be added to the text being searched.
            # Join all the module text lines, search for the number of
            # occurrences of "(pad", and then count them.
            # A set is used so pads with the same num/name are only counted once.
            # Place the pad count before everything else so the space that
            # terminates it won't be stripped off later. This is necessary
            # so (for example) "#pads=20 " won't match "#pads=208".
            num_pads = len(
                set(re.findall(r"\(\s*pad\s+([^\s)]+)", " ".join(module_text)))
            )
            num_pads_str = f"#pads={num_pads}"

            # Create a string with the module name, library name, number of pads,
            # description and tags.
            search_text = "\n".join([num_pads_str, fp_lib, module_name])
            for line in module_text:
                if "(descr " in line or "(tags " in line:
                    search_text = "\n".join([search_text, line])

            # Search the string for a match with the search terms.
            if fullmatch(
                terms, search_text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
            ):
                yield "MODULE", fp_lib, module_text, module_name

    # At the end, all modules have been scanned and the footprint cache is valid.
    footprint_cache.valid = True


@export_to_all
def search_footprints(terms, tool=None):
    """
    Print a list of footprints with the regex term within their description/tags.
    
    Searches through all available footprint libraries for footprints matching 
    the given terms and prints the results to the console.
    
    Args:
        terms (str): Space-separated search terms to match against footprint attributes.
        tool (str, optional): The ECAD tool format for the libraries to search.
                             Defaults to the currently configured tool.
    
    Returns:
        None: Results are printed to the console.
    """

    footprints = []
    for fp in search_footprints_iter(terms, tool):
        if fp[0] == "LIB":
            print(" " * 79, f"\rSearching {fp[1]} ...", sep="", end="\r")
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
        print(f"{lib_file}: {module_name} ({descr} - {tags})")


@export_to_all
def show_footprint(lib, module_name, tool=None):
    active_logger.bare_warning("Footprint display has not been implemented.")


# Define some shortcuts.
search = search_parts
show = show_part
