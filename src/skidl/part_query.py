# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Functions for finding/displaying parts and footprints.

This module provides utilities to search for electronic parts and footprints
across libraries, and to display their details. It includes support for
regular expression searches and filtering on different properties.
"""

from collections import namedtuple
import os
import os.path
import re
import sqlite3
import sys
import threading
import time

from .logger import active_logger
from .utilities import export_to_all, fullmatch, rmv_quotes, to_list, expand_path


__all__ = ["search", "show", "PartSearchDB"]


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


def get_all_lib_files(tool=None):
    """
    Return a list of all library files in the search paths for the given tool.

    Args:
        tool (str, optional): The ECAD tool format for the libraries to search.
                             Defaults to the currently configured tool.

    Returns:
        list: A list of absolute paths to library files found in the search paths.
    """

    import skidl

    tool = tool or skidl.get_default_tool()

    # Gather all the lib files from all the directories in the search paths.
    lib_files = list()
    lib_suffixes = tuple(to_list(skidl.tools.lib_suffixes[tool]))
    for lib_dir in skidl.lib_search_paths[tool]:

        # Fully expand the path into an absolute path.
        lib_dir = expand_path(lib_dir)

        # Get all the library files in the search path.
        try:
            files = os.listdir(lib_dir)
        except (FileNotFoundError, OSError):
            active_logger.bare_warning(f"Could not open directory '{lib_dir}'")
            files = []

        files = [os.path.join(lib_dir, l) for l in files if l.endswith(lib_suffixes)]
        lib_files.extend(files)

    return lib_files


# Keep a dictionary of part search databases for different tools.
part_search_dbs = {}


class PartSearchDB:
    """
    Manage a parts search SQLite database.

    The DB contains two tables:
      - libraries(lib_file TEXT PRIMARY KEY, mtime REAL)
      - parts(id INTEGER PRIMARY KEY, part_name TEXT, lib_file TEXT, search_text TEXT)

    The DB path is taken from skidl.config.part_search_db_dir. If that attribute is
    not present, defaults to the current directory.
    """

    _lock = threading.RLock()

    def __init__(self, db_dir=None, db_name=None, tool=None):
        import skidl

        self.tool = tool or skidl.get_default_tool()

        # Resolve path to database. Libraries for each tool have their own database.
        db_name = db_name or "part_search"
        db_name = f"{db_name}_{self.tool}.db"
        db_dir = db_dir or getattr(skidl.config, "part_search_db_dir", ".")
        db_path = expand_path(os.path.join(db_dir, db_name))

        # Connect/create DB.
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()

        # Use existing database or create a new one.
        self._detect_and_init_db()

        # Update any libraries whose mtime differs from filesystem.
        self.update_libs()

    def _detect_and_init_db(self):
        """
        Create tables if they don't exist.
        """

        with self._lock:
            # Create core tables.
            self._cur.execute(
                """
                CREATE TABLE IF NOT EXISTS libraries (
                    lib_file TEXT PRIMARY KEY,
                    mtime REAL
                )
                """
            )
            self._cur.execute(
                """
                CREATE TABLE IF NOT EXISTS parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_name TEXT,
                    lib_file TEXT,
                    search_text TEXT,
                    aliases TEXT,
                    description TEXT,
                    keywords TEXT,
                    FOREIGN KEY(lib_file) REFERENCES libraries(lib_file)
                )
                """
            )
            # Try to ensure uniqueness on (part_name, lib_file) so we can use
            # INSERT OR REPLACE to update parts based on those columns.
            try:
                self._cur.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS parts_part_lib_unique
                    ON parts(part_name, lib_file)
                    """
                )
            except sqlite3.OperationalError as e:
                # If creating the unique index fails (e.g., due to existing duplicates),
                # warn the user but continue – INSERT OR REPLACE will not be available.
                active_logger.bare_warning(
                    f"Could not create unique index on parts(part_name, lib_file): {e}"
                )

            self._conn.commit()

    def _get_lib_file_status(self):
        """
        Return lists of missing, stale, and fresh library files.
        """

        missing = []
        stale = []
        fresh = []

        with self._lock:
            self._cur.execute("SELECT lib_file, mtime FROM libraries")
            rows = self._cur.fetchall()
            for row in rows:
                lib_file = row["lib_file"]
                recorded_mtime = row["mtime"]
                try:
                    if not os.path.exists(lib_file):
                        missing.append(lib_file)
                        continue
                    mtime = os.path.getmtime(lib_file)
                except OSError:
                    missing.append(lib_file)
                    continue

                if mtime != recorded_mtime:
                    stale.append(lib_file)
                else:
                    fresh.append(lib_file)

        return missing, stale, fresh

    def load_from_lib_search_paths(self):
        """
        Load all libraries from the current skidl.lib_search_paths for the current tool.
        """

        # Get all files in the database that are fresh (up-to-date).
        fresh_files = self._get_lib_file_status()[2]

        # Update the files in the database that are not fresh.
        not_fresh_files = set(get_all_lib_files(self.tool)) - set(fresh_files)
        self.add_libs(*not_fresh_files)

    def add_libs(self, *lib_files):
        """
        Add or replace libraries listed in lib_files (iterable of filenames).
        Each lib is added or updated in the libraries table and
        its parts are added or updated in the parts table.
        """

        for lib_file in lib_files:
            self.add_lib(lib_file)

    def add_lib(self, lib_path, tool=None):
        """
        Parse the library file and insert parts into parts table. Update library mtime.
        lib_path should be an absolute path (or something SchLib can use).
        If the library is already in the database, then update it and all its parts.
        """

        from .schlib import SchLib

        # Use provided tool or fall back to the DB's tool.
        tool = tool or self.tool

        # Load the library using SchLib so it resolves and parses parts.
        lib = SchLib(filename=lib_path, tool=tool)
        # Use absolute filename stored by SchLib if present.
        abs_fn = expand_path(getattr(lib, "filename", lib_path))

        # Give some feedback so user knows something is happening.
        print(" " * 79, f"\rAdding {lib_path} ...", sep="", end="\r")

        # Compute mtime. If file missing, use current time as fallback.
        try:
            mtime = os.path.getmtime(abs_fn)
        except OSError:
            mtime = time.time()

        parts_to_insert = []
        # Parse parts to collect searchable text.
        for part in lib:
            try:
                # Partial parse to ensure aliases and description present.
                part.parse(partial_parse=True)
            except Exception:
                # Skip parts with parse errors.
                continue
            aliases = (
                " ".join(list(part.aliases)) if getattr(part, "aliases", None) else ""
            )
            descr = getattr(part, "description", "") or ""
            keywords = getattr(part, "keywords", "") or ""
            # Build search text: name, aliases, description, keywords.
            search_text = " ".join(filter(None, [part.name, aliases, descr, keywords]))
            parts_to_insert.append((part.name, abs_fn, search_text, aliases, descr, keywords))

        with self._lock:
            # Insert/update library record.
            self._cur.execute(
                "INSERT OR REPLACE INTO libraries(lib_file, mtime) VALUES(?, ?)",
                (abs_fn, mtime),
            )
            # Bulk insert parts using INSERT OR REPLACE so entries keyed by
            # (part_name, lib_file) are replaced rather than duplicated.
            if parts_to_insert:
                self._cur.executemany(
                    "INSERT OR REPLACE INTO parts(part_name, lib_file, search_text, aliases, description, keywords) VALUES(?, ?, ?, ?, ?, ?)",
                    parts_to_insert,
                )
                self._conn.commit()
            else:
                # No parts found: commit library entry change.
                self._conn.commit()

    def update_libs(self):
        """
        For every library recorded in the DB, compare filesystem mtime; if different, update.
        """

        missing, stale, fresh = self._get_lib_file_status()
        self.rmv_libs(*missing)
        self.add_libs(*stale)

    def rmv_libs(self, *lib_files):
        """
        Remove libraries listed in lib_files (iterable of filenames).
        Each lib and its parts are removed from the database.
        """

        for lib_file in lib_files:
            self.rmv_lib(lib_file)

    def rmv_lib(self, lib_file):
        """
        Remove a single library file and its parts from the database.
        """

        # Expand path and resolve via SchLib to get absolute filename.
        from .schlib import SchLib

        # Use SchLib to resolve the filename (it will raise if not found).
        try:
            lib = SchLib(filename=lib_file, tool=self.tool)
            # Use absolute path recorded in SchLib.filename if available.
            resolved = getattr(lib, "filename", lib_file)
        except Exception:
            # Fall back to the raw lib_file path (maybe it's already absolute).
            resolved = lib_file

        resolved = expand_path(resolved)

        with self._lock:
            self._cur.execute("DELETE FROM parts WHERE lib_file = ?", (resolved,))
            self._cur.execute("DELETE FROM libraries WHERE lib_file = ?", (resolved,))
            self._conn.commit()

    def _tokenize_query(self, query):
        """
        Parse query into a list of OR-groups, each group is list of terms (phrases kept).
        '|' separates OR groups. Quoted phrases are preserved.
        """

        or_terms = []
        # Split by '|' to produce OR groups.
        or_groups = [g.strip() for g in re.split(r"\s*\|\s*", query) if g.strip()]
        for g in or_groups:
            and_terms = []
            for m in re.finditer(r'(?:"([^"]+)"|\'([^\']+)\'|(\S+))', g):
                # double-quoted, single-quoted, or non-white character string.
                term = m.group(1) or m.group(2) or m.group(3)
                and_terms.append(term)
            if and_terms:
                or_terms.append(and_terms)
        return or_terms

    def search(self, query, limit=None):
        """
        Search parts for the given query string.
        Supports quoted phrases and '|' as OR.

        Returns a list of (part_name, lib_file) tuples for matches.
        """

        # Define a named tuple for the search results.
        # The lib_path element will actually be the contents of the lib_file field.
        # The lib_file element will be the library file name (path without the preceding path).
        # The lib_name element will be the library file name without the suffix.
        PartResult = namedtuple('PartResult', ['part_name', 'lib_path', 'lib_file', 'lib_name', 'aliases', 'description', 'keywords'])
        
        if not query or not query.strip():
            return []

        tokens_groups = self._tokenize_query(query)

        with self._lock:
            where_clauses = []
            params = []
            for group in tokens_groups:
                subclauses = []
                for term in group:
                    subclauses.append("search_text LIKE ?")
                    params.append(f"%{term}%")
                where_clauses.append("(" + " AND ".join(subclauses) + ")")
            where_sql = " OR ".join(where_clauses)
            sql = f"SELECT part_name, lib_file, aliases, description, keywords FROM parts WHERE {where_sql}"
            if limit:
                sql += f" LIMIT {int(limit)}"
            self._cur.execute(sql, params)
            rows = self._cur.fetchall()

        return [PartResult(r["part_name"], r["lib_file"], 
                           os.path.basename(r["lib_file"]), 
                           os.path.splitext(os.path.basename(r["lib_file"]))[0],
                           r["aliases"], r["description"], r["keywords"]) for r in rows]

    def close(self):
        """
        Close the database connection.
        """

        try:
            self._conn.commit()
            self._conn.close()
        except Exception:
            pass

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


@export_to_all
def search_parts(terms, tool=None, fmt=None, file=None):
    """
    Print a list of parts with the regex terms within their name, alias, description or keywords.

    Searches through all available libraries for parts matching the given terms and prints
    the results to the console.

    Args:
        terms (str): Search terms separated by spaces (AND) or | (OR) to match against part attributes.
        tool (str, optional): The ECAD tool format for the libraries to search.
                             Defaults to the currently configured tool.
        fmt (str, optional): A format string for displaying each part.
                             Defaults to "{lib_name}: {part_name} ({description})".
        file (file-like object, optional): The output stream to write results to.
                                          Defaults to sys.stdout.

    Returns:
        None: Results are printed to the console.
    """

    import skidl

    tool = tool or skidl.get_default_tool()
    fmt = fmt or "{lib_name}: {part_name} ({description})"
    file = file or sys.stdout

    if tool not in part_search_dbs:
        # Initialize and store the DB object for this tool.
        part_search_dbs[tool] = PartSearchDB(tool=tool)
    
    # Load the database from the current library search paths for the given tool.
    part_search_dbs[tool].load_from_lib_search_paths()

    # Search the database for parts matching the search terms.
    parts = part_search_dbs[tool].search(terms)

    # Output the search results sorted by lib file path and part name.
    for part in sorted(parts, key=lambda p: (p.lib_path, p.part_name)):
        part_name = part.part_name
        lib_path = part.lib_path
        lib_file = part.lib_file
        lib_name = part.lib_name
        description = part.description
        aliases = part.aliases
        keywords = part.keywords
        print(fmt.format(**locals()), file=file)

    return


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
        path = expand_path(path)

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
            uri = expand_path(uri)

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
