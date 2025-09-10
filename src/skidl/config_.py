# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Configuration management for SKiDL.

This module provides classes for loading, storing, and accessing SKiDL configuration
parameters. Configuration data is stored in JSON files and includes settings for
default tools, library search paths, footprint search paths, and backup library options.
The module supports configuration hierarchies with system, user, and project-specific 
settings that are merged according to priority.
"""

import collections
import json
import os
import os.path
import sys

from .logger import active_logger
from .part_query import footprint_cache
from .scriptinfo import get_script_name
from .tools import ALL_TOOLS, lib_suffixes, tool_modules
from .utilities import TriggerDict, export_to_all, merge_dicts, expand_path

def _get_default_skidl_storage_dir():
    """
    Return path to a platform-appropriate per-user directory for persistent SKiDL data.

    Linux/Unix: XDG_DATA_HOME/skidl or ~/.local/share/skidl
    macOS: ~/Library/Application Support/skidl
    Windows: %APPDATA%/skidl or %LOCALAPPDATA%/skidl (fallback to ~/AppData/Roaming/skidl)
    """

    # Determine the base directory for storing SKiDL data for a given OS.
    if os.name == "nt":
        appdata = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
        if appdata:
            return os.path.join(appdata, "skidl")
        return os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "skidl")
    else:
        xdg = os.getenv("XDG_DATA_HOME")
        if xdg:
            return os.path.join(xdg, "skidl")
        if sys.platform == "darwin":
            return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "skidl")
        return os.path.join(os.path.expanduser("~"), ".local", "share", "skidl")

@export_to_all
class Config(dict):
    """
    Base class for managing configuration parameters.
    
    This class extends the dictionary to store configuration parameters and provides
    methods to load configuration from JSON files and save it back to disk.
    Configuration from multiple sources can be merged with intelligent handling
    of nested dictionaries.
    
    Args:
        cfg_file_name (str): Name of the configuration file.
        *dirs: Directories to search for configuration files.
    """

    def __init__(self, cfg_file_name, *dirs):
        super().__init__()
        self.cfg_file_name = cfg_file_name
        self.load(*dirs)

    def __getattr__(self, key):
        """
        Access configuration values as attributes.
        
        This enables dot notation access to configuration parameters in addition
        to dictionary-style access.
        
        Args:
            key (str): The configuration parameter name.
            
        Returns:
            The value of the configuration parameter.
            
        Raises:
            AttributeError: If the key doesn't exist in the configuration.
        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        """
        Set configuration values as attributes and dictionary entries.
        
        This ensures that attribute-style and dictionary-style access and
        modification are synchronized.
        
        Args:
            key (str): The configuration parameter name.
            value: The value to assign to the parameter.
        """
        self.__dict__[key] = value
        self[key] = value

    def merge(self, merge_dct):
        """
        Merge another dictionary into this configuration.
        
        This method recursively merges dictionaries, preserving nested structures
        where possible.
        
        Args:
            merge_dct (dict): Dictionary to merge into this configuration.
        """
        for k, v in list(merge_dct.items()):
            if (
                k in self
                and isinstance(self[k], dict)
                and isinstance(merge_dct[k], collections.abc.Mapping)
            ):
                merge_dicts(self[k], merge_dct[k])
            else:
                self[k] = merge_dct[k]

    def load(self, *dirs):
        """
        Load configuration from JSON files in the specified directories.
        
        This method looks for the configuration file in each directory and merges
        the settings found in each file, with later directories taking precedence.
        
        Args:
            *dirs: Directories to search for configuration files.
        """
        for dir in dirs:
            path = expand_path(os.path.join(dir, self.cfg_file_name))
            try:
                with open(path) as cfg_fp:
                    self.merge(json.load(cfg_fp))
            except (FileNotFoundError, IOError):
                pass

    def store(self, dir="."):
        """
        Store the current configuration as a JSON file.
        
        Args:
            dir (str, optional): Directory to store the configuration file in.
                Defaults to the current directory.
        """
        path = expand_path(os.path.join(dir, self.cfg_file_name))
        with open(path, "w") as cfg_fp:
            json.dump(self, cfg_fp, indent=4)


@export_to_all
class SkidlConfig(Config):
    """
    Configuration class specialized for SKiDL.
    
    This class extends the base Config class with SKiDL-specific defaults and
    behaviors, such as managing tool selection, library paths, and footprint paths.
    
    Args:
        tool (str): Default tool/backend to use if not specified in config files.
    """

    def __init__(self, tool):
        from skidl import SKIDL

        self.skidl_storage_dir = _get_default_skidl_storage_dir()

        # Load the .skidlcfg file from one of the list of directories.
        super().__init__(".skidlcfg", "/etc", self.skidl_storage_dir, ".")

        # Make the directory for storing persistent SKiDL data if it doesn't exist.
        os.makedirs(self.skidl_storage_dir, exist_ok=True)

        # If no configuration files were found, set default backend/tool.
        if "tool" not in self:
            self.tool = tool

        # If no configuration files were found, set default directory for part library pickle files.
        if "pickle_dir" not in self:
            self.pickle_dir = os.path.join(self.skidl_storage_dir, "lib_pickle_dir")
        # Make the directory.
        os.makedirs(self.pickle_dir, exist_ok=True)

        # If no configuration files were found, set default directory for part search database.
        if "part_search_db_dir" not in self:
            self.part_search_db_dir = self.skidl_storage_dir
        # Make the directory.
        os.makedirs(self.part_search_db_dir, exist_ok=True)

        # If no configuration files were found, set some default part lib search paths.
        if "lib_search_paths" not in self:
            self["lib_search_paths"] = {
                tool: tool_modules[tool].default_lib_paths() for tool in ALL_TOOLS
            }

        # If no configuration files were found, set base name of default backup part library.
        if "backup_lib_name" not in self:
            self.backup_lib_name = get_script_name()
        if "backup_lib_file_name" not in self:
            self.backup_lib_file_name = self.backup_lib_name + lib_suffixes[SKIDL]
        if "query_backup_lib" not in self:
            self.query_backup_lib = True
        if "backup_lib" not in self:
            self.backup_lib = None

        # If no configuration files were found, set some default footprint search paths.
        if "footprint_search_paths" not in self:
            self["footprint_search_paths"] = {
                tool: tool_modules[tool].get_fp_lib_tbl_dir() for tool in ALL_TOOLS
            }

        # Cause the footprint cache to be invalidated if the footprint search path changes.
        def invalidate_footprint_cache(self, k, v):
            footprint_cache.reset()

        self["footprint_search_paths"] = TriggerDict(self["footprint_search_paths"])
        self["footprint_search_paths"].trigger_funcs[self.tool] = invalidate_footprint_cache

    def store(self, dir=None):
        """
        Store the current SKiDL configuration as a JSON file.
        
        Args:
            dir (str, optional): Directory to store the configuration file in.
                Defaults to the SKiDL storage directory.
        """
        dir = dir or self.skidl_storage_dir
        super().store(dir)
