# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Routines for getting information about a running script.

This module provides functions to determine information about the currently
executing Python script, such as its name, directory, and call stack. These 
functions are useful for generating file names based on the script name and
for debugging purposes.
"""

import inspect
import os
import sys
import traceback

from .utilities import export_to_all


@export_to_all
def scriptinfo():
    """
    Get information about the running top-level Python script.
    
    This function identifies the top-level script that is currently running,
    whether it's an interpreted Python script or a compiled executable.
    
    Returns:
        dict: A dictionary with the following keys:
            - 'dir': Directory containing the script or compiled executable
            - 'name': Name of script or executable
            - 'source': Name of source code file
            
    Notes:
        'name' and 'source' are identical if and only if running interpreted code.
        When running code compiled by `py2exe` or `cx_freeze`, `source` contains
        the name of the originating Python script.
        If compiled by PyInstaller, `source` contains no meaningful information.
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
    """
    Return the name of the top-level script without the file extension.
    
    This function gets the name of the top-level script that is currently running
    and removes any file extension.
    
    Returns:
        str: The name of the top-level script without file extension.
    """
    return os.path.splitext(scriptinfo()["name"])[0]


@export_to_all
def get_skidl_trace(track_abs_path=False):
    """
    Return a list containing the source line trace where a SKiDL object was instantiated.
    
    This function traces the call stack to determine where a SKiDL object was created,
    skipping internal SKiDL function calls to show only the user's code.
    
    Returns:
        list: A list of strings in the format "filepath:line_number" representing
              the call stack that led to the creation of a SKiDL object.
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
        if track_abs_path:
            filepath = os.path.abspath(filename)
        else:
            filepath = os.path.relpath(filename, skidl_dir)
        skidl_trace.append(":".join((filepath, str(lineno))))

    return skidl_trace
