# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2019 by XESS Corp.
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
Routines for getting information about a script.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import inspect
import os
import sys
import traceback
from builtins import str

from future import standard_library

standard_library.install_aliases()


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

    # trc contains highest level calling script name
    # check if we have been compiled
    if getattr(sys, "frozen", False):
        scriptdir, scriptname = os.path.split(sys.executable)
        return {"dir": scriptdir, "name": scriptname, "source": trc}

    # from here on, we are in the interpreted case
    scriptdir, trc = os.path.split(trc)
    # if trc did not contain directory information,
    # the current working directory is what we need
    if not scriptdir:
        scriptdir = os.getcwdu()

    scr_dict = {"name": trc, "source": trc, "dir": scriptdir}
    return scr_dict


def get_script_name():
    """Return the name of the top-level script."""
    return os.path.splitext(scriptinfo()["name"])[0]


def get_skidl_trace():
    """
    Return a string containing the source line trace where a SKiDL object was instantiated.
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

    # Record file_name#line_num starting from the bottom of the stack
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
        skidl_trace.append("#".join((filepath, str(lineno))))

    return ";".join(skidl_trace)
