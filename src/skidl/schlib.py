# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Handles schematic libraries for various ECAD tools.
"""

import re

from .alias import Alias
from .logger import active_logger
from .utilities import (
    consistent_hash,
    cnvt_to_var_name,
    export_to_all,
    filter_list,
    flatten,
    is_url,
    list_or_scalar,
    opened,
    get_abs_filename,
    norecurse,
)


@export_to_all
class SchLib(object):
    """
    A class for storing parts from a schematic component library file.

    Attributes:
        filename: The name of the file from which the parts were read.
        parts: The list of parts (composed of Part objects).

    Args:
        filename: The name of the library file.
        tool: The format of the library file (e.g., KICAD).
        lib_section: The section of the library to access (for SPICE, only).
        use_cache: If true, use a cache of libraries to speed up loading.
        use_pickle: If true, pickle the library for faster loading next time.

    Keyword Args:
        attribs: Key/value pairs of attributes to add to the library.
    """

    # Keep a dict of filenames and their associated SchLib object
    # for fast loading of libraries.
    _cache = {}

    def __init__(
        self,
        filename=None,
        tool=None,
        lib_section=None,
        use_cache=True,
        use_pickle=True,
        **attribs
    ):
        """
        Load the parts from a library file.
        """

        import os
        import pickle
        import skidl

        from .tools import tool_modules, lib_suffixes

        tool = tool or skidl.config.tool

        # Library starts off empty of parts.
        self.parts = []

        # Attach attributes to the library.
        for k, v in list(attribs.items()):
            setattr(self, k, v)

        # If no filename, just create an empty library and exit.
        if not filename:
            return

        # Get the absolute path for the part library file.
        try:
            paths = skidl.lib_search_paths[tool]
            exts = lib_suffixes[tool]
        except KeyError:
            # OK, unknown tool...
            active_logger.raise_(
                ValueError,
                "Unsupported ECAD tool library: {}.".format(tool),
            )
        abs_filename = get_abs_filename(
            filename, paths, exts, allow_failure=False, descend=-1
        )

        # Don't pickle files stored in remote repos because it's difficult to
        # get their modification times to compare against the local pickled library
        # to see which is fresher. So remote libs are never pickled.
        # TODO: Allow pickling of remote part libraries.
        use_pickle = use_pickle and not is_url(abs_filename)

        # Get a unique hash to reference the part library file.
        abs_fn_hash = consistent_hash(abs_filename)

        # Create the absolute file name of the pickle file for storing this part library.
        # The pickle file name is based on the library name, the tool name, and the hash.
        # It is stored in a directory specified in the SKIDL configuration file.
        lib_name, lib_ext = os.path.splitext(os.path.split(abs_filename)[1])
        lib_pickle_abs_fn = os.path.abspath(os.path.join(
            skidl.config.pickle_dir, "_".join((lib_name, tool, str(abs_fn_hash)))
        ) + ".pkl")

        # Load this SchLib with an existing SchLib object if the file name hash
        # matches one in the cache.
        if lib_pickle_abs_fn in self._cache:
            self.__dict__.update(self._cache[lib_pickle_abs_fn].__dict__)

        # Load this Schlib from the pickle file if it exists and it's more recent
        # than the original part library file.
        elif (
            use_pickle
            and os.path.exists(lib_pickle_abs_fn)
            and os.path.getmtime(lib_pickle_abs_fn) >= os.path.getmtime(abs_filename)
        ):
            with open(lib_pickle_abs_fn, "rb") as f:
                self.__dict__.update(pickle.load(f).__dict__)
            # Cache a reference to the library.
            if use_cache:
                self._cache[lib_pickle_abs_fn] = self

        # Otherwise, load from a schematic part library file.
        else:
            # Use the tool name to find the function for loading the library.
            tool_modules[tool].load_sch_lib(
                self,
                abs_filename,
                # skidl.lib_search_paths[tool],
                lib_section=lib_section,
            )
            self.filename = filename
            # Cache a reference to the library.
            if use_cache:
                self._cache[lib_pickle_abs_fn] = self
            # Pickle the library for future use.
            if use_pickle:
                if not os.path.exists(skidl.config.pickle_dir):
                    os.mkdir(skidl.config.pickle_dir)
                with open(lib_pickle_abs_fn, "wb") as f:
                    try:
                        pickle.dump(self, f)
                    except Exception as e:
                        pass
                # Delete the pickled lib if its size if zero (i.e., a pickling error occurred).
                if os.path.exists(lib_pickle_abs_fn):
                    if os.path.getsize(lib_pickle_abs_fn) == 0:
                        # Delete the file
                        os.remove(lib_pickle_abs_fn)

    def __str__(self):
        """Return a list of the part names in this library as a string."""
        return "\n".join(["{}: {}".format(p.name, p.description) for p in self.parts])

    __repr__ = __str__

    def __len__(self):
        """
        Return number of parts in library.
        """
        return len(self.parts)

    def __getitem__(self, id):
        """Get part by name or alias."""
        return list_or_scalar(self.get_parts_by_name(id))

    def __iadd__(self, *parts):
        """Add one or more parts to a library."""
        return self.add_parts(*parts)

    @classmethod
    def reset(cls):
        """Clear the cache of processed library files."""
        cls._cache = {}

    def add_parts(self, *parts):
        """Add one or more parts to a library."""

        from .part import TEMPLATE

        for part in flatten(parts):
            # Parts with the same name are not allowed in the library.
            if not self.get_parts_by_name(
                part.name, be_thorough=False, allow_failure=True
            ):
                self.parts.append(part.copy(dest=TEMPLATE))
                # Place a pointer to this library into the added part.
                self.parts[-1].lib = self
        return self

    def get_parts(self, use_backup_lib=True, **criteria):
        """
        Return parts from a library that match *all* the given criteria.

        Keyword Args:
            criteria: One or more keyword-argument pairs. The keyword specifies
                the attribute name while the argument contains the desired value
                of the attribute.

        Returns:
            A list of Parts that match all the criteria.
        """

        import skidl

        parts = filter_list(self.parts, **criteria)
        if not parts and use_backup_lib and skidl.config.query_backup_lib:
            try:
                backup_lib = load_backup_lib()
                parts = backup_lib.get_parts(use_backup_lib=False, **criteria)
            except AttributeError:
                pass
        return parts

    def get_parts_quick(self, name):
        """Do a quick search for a part name or alias."""
        return [prt for prt in self.parts if prt.aliases == name]

    def get_parts_by_name(
        self,
        name,
        be_thorough=True,
        allow_multiples=False,
        allow_failure=False,
        partial_parse=False,
    ):
        """
        Return a Part with the given name or alias from the part list.

        Args:
            name: The part name or alias to search for in the library.
            be_thorough: Do thorough search, not just simple string matching.
            allow_multiples: If true, return a list of parts matching the name.
                If false, return only the first matching part and issue
                a warning if there were more than one.
            allow_failure: Return None if no matches found. Issue no errors/warnings.
            partial_parse: If true, don't fully parse any parts that are found.

        Returns:
            A list of Parts that match all the criteria.
        """

        # Start with a simple search for the part name.
        names = Alias(name, name.lower(), name.upper())
        parts = self.get_parts_quick(names)

        # Simple search failed, so try the more thorough search method.
        if not parts and be_thorough:
            parts = self.get_parts(aliases=name)

        # No parts found, so signal an error.
        if not parts and not allow_failure:
            message = "Unable to find part {} in library {}.".format(
                name, getattr(self, "filename", "UNKNOWN")
            )
            active_logger.raise_(ValueError, message)

        if len(parts) > 1 and not allow_multiples:
            message = "Found multiple parts matching {}. Selecting {}.".format(
                name, parts[0].name
            )
            active_logger.warning(message)
            parts = parts[0:1]  # Just keep the first part.

        # Do whatever parsing was requested for the found parts.
        for part in parts:
            part.parse(partial_parse)

        return parts

    def export(self, libname, file_=None, tool=None, addtl_part_attrs=None):
        """
        Export a library into a file.

        Args:
            libname: A string containing the name of the library.
            file_: The file the library will be exported to. It can either
                be a file object or a string or None. If None, the file
                will be the same as the library name with the library
                suffix appended.
            tool: The CAD tool library format to be used. Currently, this can
                only be SKIDL.
            addtl_part_attrs (list): List of additional part attribute names to include in export.
        """

        def prettify(s):
            """Breakup and indent library export string."""
            s = re.sub(r"(Part\()", r"\n        \1", s)
            s = re.sub(r"(Pin\()", r"\n            \1", s)
            return s

        from skidl import SKIDL
        from skidl.tools import lib_suffixes

        if tool is None:
            tool = SKIDL

        file_ = file_ or (libname + lib_suffixes[tool])

        export_str = "from collections import defaultdict\n"
        export_str += "from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE\n\n"
        export_str += "from skidl.pin import pin_types\n\n"
        export_str += "SKIDL_lib_version = '0.0.1'\n\n"
        part_export_str = ",".join(
            [p.export(addtl_part_attrs=addtl_part_attrs) for p in self.parts]
        )
        export_str += "{} = SchLib(tool=SKIDL).add_parts(*[{}])".format(
            cnvt_to_var_name(libname), part_export_str
        )
        export_str = prettify(export_str)
        with opened(file_, "w") as f:
            f.write(export_str)


@export_to_all
@norecurse
def load_backup_lib():
    """Load a backup library that stores the parts used in the circuit."""

    from . import skidl

    # Don't keep reloading the backup library once it's loaded.
    if not skidl.config.backup_lib:
        try:
            # The backup library is a SKiDL lib stored as a Python module.
            glb_vars, loc_vars = None, locals()
            exec(open(skidl.config.backup_lib_file_name).read(), glb_vars, loc_vars)
            # Copy the backup library in the local storage to the global storage.
            skidl.config.backup_lib = loc_vars[skidl.config.backup_lib_name]

        except (FileNotFoundError, ImportError, NameError, IOError):
            pass

    return skidl.config.backup_lib
