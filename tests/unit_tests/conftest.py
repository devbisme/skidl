# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

from pathlib import Path
import pytest
import os

from skidl import *
from skidl.tools import ALL_TOOLS
from skidl.logger import rt_logger, erc_logger
from skidl.config_ import SkidlConfig

files_at_start = set([])

def setup_function():
    # Record files originally in directory so we know which ones not to delete.
    global files_at_start
    files_at_start = set(os.listdir(os.getcwd()))

    config = SkidlConfig(KICAD) # Sets default tool.

    # Set library search paths from config file.
    for tool in lib_search_paths:
        lib_search_paths[tool] = config.lib_search_paths[tool]

    # Mini-reset to remove circuitry but retain any loaded libraries.
    default_circuit.mini_reset()

    # Turn on backup part library creation.
    skidl.config.query_backup_lib = True

    # Clear any logger errors and warnings.
    rt_logger.error.reset()
    rt_logger.warning.reset()
    erc_logger.error.reset()
    erc_logger.warning.reset()

    # Set the default tool for the test suite from the env variable SKIDL_TOOL.
    tool = {
        "SKIDL": SKIDL,
        "SPICE": SPICE,
        "KICAD5": KICAD5,
        "KICAD6": KICAD6,
        "KICAD7": KICAD7,
        "KICAD8": KICAD8,
        "KICAD9": KICAD9,
    }.get(os.getenv("SKIDL_TOOL"), KICAD9)
    set_default_tool(tool)


def teardown_function():
    # Delete files created during testing.
    files_at_end = set(os.listdir(os.getcwd()))
    for file in files_at_end - files_at_start:
        try:
            os.remove(file)
        except Exception:
            pass

@pytest.fixture(autouse=True)
def setup_teardown():
    """Automatically run setup and teardown for all tests."""
    setup_function()
    yield
    teardown_function()

@pytest.fixture(scope="session", autouse=True)
def cleanup_pkl_files():
    """
    Session-scoped fixture that automatically runs after all tests complete.
    Removes all .pkl files in the current directory and subdirectories.
    The autouse=True parameter means it will run automatically without needing
    to be explicitly included in test functions.
    """
    # This will run before any tests
    yield
    
    # This will run after all tests complete
    current_dir = Path('.')
    pkl_files = current_dir.glob('**/*.pkl')
    
    for pkl_file in pkl_files:
        try:
            pkl_file.unlink()
        except Exception as e:
            pass
