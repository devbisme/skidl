# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Routines for getting information about a script.
"""
from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import inspect
import os
import sys
import traceback
from builtins import str

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .utilities import export_to_all



@export_to_all
def scriptinfo():
    """
    Returns a dictionary with information about the running top level Python
    script:
    ---------------------------------------------------------------------------
    dir:    directory containing script or compiled executable
    name:   name of script or executable
    source: name of source code file
    ---------------------------------------------------------------------------
    `name` and `source` are identical if and only if running interpreted code.
    When running code compiled by `py2exe` or `cx_freeze`, `source` contains
    the name of the originating Python script.
    If compiled by PyInstaller, `source` contains no meaningful information.

    Downloaded from:
    http://code.activestate.com/recipes/579018-python-determine-name-and-directory-of-the-top-lev/
    """

    # ---------------------------------------------------------------------------
    # scan through call stack for caller information
    # ---------------------------------------------------------------------------
    trc = "skidl"  # Make sure this gets set to something when in interactive mode.
    for teil in inspect.stack():
        # skip system calls
        if teil[1].startswith("<"):
            continue
        if teil[1].upper().startswith(sys.exec_prefix.upper()):
            continue
        trc = teil[1]

    # trc contains highest level calling script name.
    # Check if we have been compiled.
    if getattr(sys, "frozen", False):
        scriptdir, scriptname = os.path.split(sys.executable)
        return {"dir": scriptdir, "name": scriptname, "source": trc}

    # From here on, we are in the interpreted case
    scriptdir, trc = os.path.split(trc)
    # If trc did not contain directory information,
    # the current working directory is what we need
    scriptdir = scriptdir or os.getcwd()

    scr_dict = {"name": trc, "source": trc, "dir": scriptdir}
    return scr_dict


@export_to_all
def get_script_name():
    """Return the name of the top-level script."""
    return os.path.splitext(scriptinfo()["name"])[0]


@export_to_all
def get_skidl_trace():
    """
    Return a list containing the source line trace where a SKiDL object was instantiated.
    """

    # To determine where this object was created, trace the function
    # calls that led to it and place into a field
    # but strip off all the calls to internal SKiDL functions.

    call_stack = inspect.stack()  # Get function call stack.

    # Use the function at the top of the stack to
    # determine the location of the SKiDL library functions.
    try:
        skidl_dir, _ = os.path.split(call_stack[0].filename)
    except AttributeError:
        skidl_dir, _ = os.path.split(call_stack[0][1])

    # Record file_name:line_num starting from the bottom of the stack
    # and terminate as soon as a function is found that's in the
    # SKiDL library (no use recording internal calls).
    skidl_trace = []
    for frame in reversed(call_stack):
        try:
            filename = frame.filename
            lineno = frame.lineno
        except AttributeError:
            filename = frame[1]
            lineno = frame[2]
        if os.path.split(filename)[0] == skidl_dir:
            # Found function in SKiDL library, so trace is complete.
            break

        # Get the absolute path to the file containing the function
        # and the line number of the call in the file. Append these
        # to the trace.
        filepath = os.path.abspath(filename)
        skidl_trace.append(":".join((filepath, str(lineno))))

    return skidl_trace
