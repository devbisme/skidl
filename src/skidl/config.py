# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Handles configuration parameters stored in a JSON file.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import collections
import json
import os.path
from builtins import open, super

from future import standard_library

from .logger import active_logger
from .part_query import footprint_cache
from .tools import ALL_TOOLS, KICAD, SKIDL
from .tools.kicad import get_kicad_lib_tbl_dir
from .utilities import TriggerDict, export_to_all, merge_dicts

standard_library.install_aliases()


@export_to_all
class Config(dict):
    """Class for handling configuration parameters."""

    def __init__(self, cfg_file_name, *dirs):
        super().__init__()
        self.cfg_file_name = cfg_file_name
        self.load(*dirs)

    def merge(self, merge_dct):
        """Recurse through both dicts and updates keys."""
        for k, v in list(merge_dct.items()):
            if (
                k in self
                and isinstance(self[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)
            ):
                merge_dicts(self[k], merge_dct[k])
            else:
                self[k] = merge_dct[k]

    def load(self, *dirs):
        """Load configuration from JSON files in given dirs."""
        for dir in dirs:
            path = os.path.join(dir, self.cfg_file_name)
            path = os.path.expanduser(path)
            path = os.path.abspath(path)
            try:
                with open(path) as cfg_fp:
                    self.merge(json.load(cfg_fp))
            except (FileNotFoundError, IOError):
                pass

    def store(self, dir="."):
        """Store configuration file as JSON in directory."""
        path = os.path.join(dir, self.cfg_file_name)
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        with open(path, "w") as cfg_fp:
            json.dump(self, cfg_fp, indent=4)


@export_to_all
class SkidlConfig(Config):
    """Config specialized for SKiDL configuration files."""

    def __init__(self):
        super().__init__(".skidlcfg", "/etc", "~", ".")

        # If no configuration files were found, set some default lib search paths.
        if "lib_search_paths" not in self:

            # No lib search paths, so start with the current directory for all tools.
            self["lib_search_paths"] = {tool: ["."] for tool in ALL_TOOLS}

            # Add the location of the default KiCad part libraries.
            try:
                self["lib_search_paths"][KICAD].append(os.environ["KICAD_SYMBOL_DIR"])
            except KeyError:
                active_logger.warning(
                    "KICAD_SYMBOL_DIR environment variable is missing, so the default KiCad symbol libraries won't be searched."
                )

            # Add the location of the default SKiDL part libraries.
            default_skidl_libs = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "libs"
            )
            self["lib_search_paths"][SKIDL].append(default_skidl_libs)

        # If no configuration files were found, set some default footprint search paths.
        if "footprint_search_paths" not in self:
            dir_ = get_kicad_lib_tbl_dir()
            self["footprint_search_paths"] = {tool: [dir_] for tool in ALL_TOOLS}

        # Cause the footprint cache to be invalidated if the footprint search path changes.
        def invalidate_footprint_cache(self, k, v):
            footprint_cache.reset()

        self["footprint_search_paths"] = TriggerDict(self["footprint_search_paths"])
        self["footprint_search_paths"].trigger_funcs[KICAD] = invalidate_footprint_cache
