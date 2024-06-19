# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

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

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .logger import active_logger
from .part_query import footprint_cache
from .scriptinfo import get_script_name
from .tools import ALL_TOOLS, lib_suffixes, tool_modules
from .utilities import TriggerDict, export_to_all, merge_dicts


@export_to_all
class Config(dict):
    """Class for handling configuration parameters."""

    def __init__(self, cfg_file_name, *dirs):
        super().__init__()
        self.cfg_file_name = cfg_file_name
        self.load(*dirs)

    def __getattr__(self, key):
        """Get the value of a Config attribute or else from the Config dictionary."""
        try:
            return self[key]
        except KeyError:
            raise AttributeError
        
    def __setattr__(self, key, value):
        """Set the value of both a Config attribute and a Config dictionary entry."""
        self.__dict__[key] = value
        self[key] = value

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
        from skidl import SKIDL, KICAD

        super().__init__(".skidlcfg", "/etc", "~", ".")

        # If no configuration files were found, set default backend/tool.
        if "tool" not in self:
            self.tool = KICAD

        # If no configuration files were found, set some default part lib search paths.
        if "lib_search_paths" not in self:
            self["lib_search_paths"] = {tool: tool_modules[tool].default_lib_paths() for tool in ALL_TOOLS}

        # If no configuration files were found, set base name of default backup part library.
        if "backup_lib_name" not in self:
            self.backup_lib_name = get_script_name() + "_lib"
        if "backup_lib_file_name" not in self:
            self.backup_lib_file_name = self.backup_lib_name + lib_suffixes[SKIDL]
        if "query_backup_lib" not in self:
            self.query_backup_lib = True
        if "backup_lib" not in self:
            self.backup_lib = None

        # If no configuration files were found, set some default footprint search paths.
        if "footprint_search_paths" not in self:
            self["footprint_search_paths"] = {tool: tool_modules[tool].get_fp_lib_tbl_dir() for tool in ALL_TOOLS}

        # Cause the footprint cache to be invalidated if the footprint search path changes.
        def invalidate_footprint_cache(self, k, v):
            footprint_cache.reset()

        self["footprint_search_paths"] = TriggerDict(self["footprint_search_paths"])
        self["footprint_search_paths"].trigger_funcs[KICAD] = invalidate_footprint_cache
