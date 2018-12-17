# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2016 by XESS Corp.
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
Utility functions used by the rest of SKiDL.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import super
from builtins import open
from builtins import int
from builtins import dict
from builtins import str
from builtins import zip
from builtins import range
from builtins import object
from future import standard_library
standard_library.install_aliases()

import sys
import os
import os.path
import re
import logging
import inspect
import traceback
from contextlib import contextmanager

from .py_2_3 import *

"""Separator for strings containing multiple indices."""
INDEX_SEPARATOR = ','


def norecurse(f):
    """Decorator that keeps a function from recursively calling itself.

    Parameters
    ----------
    f: function
    """

    def func(*args, **kwargs):
        # If a function's name is on the stack twice (once for the current call
        # and a second time for the previous call), then return without
        # executing the function.
        if len([1 for l in traceback.extract_stack()
                if l[2] == f.__name__]) > 1:
            return None

        # Otherwise, not a recursive call so execute the function and return result.
        return f(*args, **kwargs)

    return func


class CountCalls(object):
    """Decorator for counting the number of times a function is called.

    This is used for counting errors and warnings passed to logging functions,
    making it easy to track if and how many errors/warnings were issued.
    """

    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)


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

    #---------------------------------------------------------------------------
    # scan through call stack for caller information
    #---------------------------------------------------------------------------
    trc = 'skidl'  # Make sure this gets set to something when in interactive mode.
    for teil in inspect.stack():
        # skip system calls
        if teil[1].startswith("<"):
            continue
        if teil[1].upper().startswith(sys.exec_prefix.upper()):
            continue
        trc = teil[1]

    # trc contains highest level calling script name
    # check if we have been compiled
    if getattr(sys, 'frozen', False):
        scriptdir, scriptname = os.path.split(sys.executable)
        return {"dir": scriptdir, "name": scriptname, "source": trc}

    # from here on, we are in the interpreted case
    scriptdir, trc = os.path.split(trc)
    # if trc did not contain directory information,
    # the current working directory is what we need
    if not scriptdir:
        scriptdir = os.getcwd()

    scr_dict = {"name": trc, "source": trc, "dir": scriptdir}
    return scr_dict


def get_script_name():
    """Return the name of the top-level script."""
    return os.path.splitext(scriptinfo()['name'])[0]


def create_logger(title, log_msg_id='', log_file_suffix='.log'):
    """
    Create a logger, usually for run-time errors or ERC violations.
    """

    logger = logging.getLogger(title)

    # Errors & warnings always appear on the terminal.
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(
        logging.Formatter(log_msg_id + '%(levelname)s: %(message)s'))
    logger.addHandler(handler)

    # Errors and warnings are stored in a log file with the top-level script's name.
    handler = logging.StreamHandler(
        open(get_script_name() + log_file_suffix, 'w'))
    handler.setLevel(logging.WARNING)
    handler.setFormatter(
        logging.Formatter(log_msg_id + '%(levelname)s: %(message)s'))
    logger.addHandler(handler)

    # Set logger to trigger on info, warning, and error messages.
    logger.setLevel(logging.INFO)

    # Augment the logger's functions to count the number of errors and warnings.
    logger.error = CountCalls(logger.error)
    logger.warning = CountCalls(logger.warning)

    return logger


###############################################################################
# Set up loggers for runtime messages and ERC reports.

logger = create_logger('skidl')
erc_logger = create_logger('ERC_Logger', 'ERC ', '.erc')

###############################################################################


def is_binary_file(filename):
    '''Return true if a file contains binary (non-text) characters.'''
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27}
                           | set(range(0x20, 0x100)) - {0x7f})
    try:
        with open(filename, 'rb') as fp:
            return bool(fp.read(1024).translate(None, text_chars))
    except (IOError, FileNotFoundError, TypeError):
        return False


def find_and_open_file(filename,
                       paths=None,
                       ext=None,
                       allow_failure=False,
                       exclude_binary=False,
                       descend=0):
    """
    Search for a file in list of paths, open it and return file pointer and full file name.

    Args:
        filename: Base file name (e.g., "my_file").
        paths: List of paths to search for the file.
        ext: The extension for the file (e.g., "txt").
        allow_failure: If false, failure to find file raises and exception.
        exclude_binary: If true, skip files that contain binary data.
        descend: If 0, don't search lower-level directories. If positive, search
                 that many levels down for the file. If negative, descend into
                 subdirectories without limit.
    """

    # If no paths are given, then just check the current directory.
    if not paths:
        paths = ['.']

    # If the filename has no extension, then give it one.
    if ext and not filename.endswith(ext):
        fn_plus_ext = filename + ext
    else:
        fn_plus_ext = filename

    # Search the paths for the file.
    for path in paths:
        if not os.path.exists(path):
            continue  # Skip paths that don't exist.
        abs_filename = os.path.join(path, fn_plus_ext)
        if not exclude_binary or not is_binary_file(abs_filename):
            try:
                # The search stops once the file is successfully opened.
                return open(abs_filename, encoding='utf8'), abs_filename
            except (IOError, FileNotFoundError, TypeError):
                pass
        # If file not found, look in subdirectories or go to next path.
        if descend:
            # Look in subdirectories.
            dir_contents = [os.path.join(path, f) for f in os.listdir(path)]
            subdirs = [f for f in dir_contents if os.path.isdir(f)]
            if subdirs:
                fp, fn = find_and_open_file(
                    filename=filename,
                    paths=subdirs,
                    ext=ext,
                    allow_failure=True,
                    exclude_binary=exclude_binary,
                    descend=descend - 1)
                if fp:
                    return fp, fn

    # Couldn't find the file.
    if allow_failure:
        return None, None
    else:
        logger.error("Can't open file: {}.\n".format(filename))
        raise FileNotFoundError


def add_unique_attr(obj, name, value):
    """Create an attribute if the attribute name isn't already used."""
    setattr(obj, name, getattr(obj, name, value))
    # if id(getattr(obj, name)) != id(value):
        # logger.warn('Unable to create attribute {name} of type {typ1} because one already exists of type {typ2} in {obj}'.format(name=name, typ1=type(value), typ2=type(getattr(obj,name)), obj=str(obj)))


def add_quotes(s):
    """Return string with added quotes if it contains whitespace or parens."""
    if not isinstance(s, basestring):
        return s
    if re.search(r'[\s()]', s):
        return '"' + s + '"'
    return s


def to_list(x):
    """
    Return x if it is already a list, or return a list if x is a scalar.
    """
    if isinstance(x, (list, tuple)):
        return x  # Already a list, so just return it.
    return [x]  # Wasn't a list, so make it into one.


def cnvt_to_var_name(s):
    """Convert a string to a legal Python variable name and return it."""
    return re.sub(r'\W|^(?=\d)', '_', s)


def list_or_scalar(lst):
    """
    Return a list if passed a multi-element list, otherwise return a single scalar.

    Args:
        lst: Either a list or a scalar.

    Returns:
        * A list if passed a multi-element list.
        * The list element if passed a single-element list.
        * None if passed an empty list.
        * A scalar if passed a scalar.
    """
    if isinstance(lst, (list, tuple)):
        if len(lst) > 1:
            return lst  # Multi-element list, so return it unchanged.
        if len(lst) == 1:
            return lst[0]  # Single-element list, so return the only element.
        return None  # Empty list, so return None.
    return lst  # Must have been a scalar, so return that.


def flatten(nested_list):
    """
    Return a flattened list of items from a nested list.
    """
    lst = []
    for item in nested_list:
        if isinstance(item, (list, tuple)):
            lst.extend(flatten(item))
        else:
            lst.append(item)
    return lst


def get_unique_name(lst, attrib, prefix, initial=None):
    """
    Return a name that doesn't collide with another in a list.

    This subroutine is used to generate unique part references (e.g., "R12")
    or unique net names (e.g., "N$5").

    Args:
        lst: The list of objects containing names.
        attrib: The attribute in each object containing the name.
        prefix: The prefix attached to each name.
        initial: The initial setting of the name (can be None or empty string).

    Returns:
        A string containing the unique name.
    """

    # If the initial name is None, then create a name based on the prefix
    # and the smallest unused number that's available for that prefix.
    if not initial:

        # Get list entries with the prefix followed by a number, e.g.: C55
        filter_dict = {attrib: re.escape(prefix) + r'\d+'}
        sub_list = filter_list(lst, **filter_dict)

        # If entries were found, then find the smallest available number.
        if sub_list:
            # Get the list of names.
            names = [getattr(item, attrib) for item in sub_list]
            # Remove the prefix from each name, leaving only the numbers.
            l = len(prefix)
            nums = set([int(n[l:]) for n in names])
            stop = max(nums) + 1
            # Generate a list of the unused numbers in the range [1,stop]
            # and select the minimum value.
            n = min(set(range(1, stop + 1)) - nums)

        # If no entries were found, start counting from 1.
        else:
            n = 1

        # The initial name is the prefix plus the number.
        initial = prefix + str(n)

    # If the initial name is just a number, then prepend the prefix to it.
    elif isinstance(initial, int):
        initial = prefix + str(initial)

    # Now determine if there are any items in the list with the same name.
    filter_dict = {attrib: re.escape(initial)}
    sub_list = filter_list(lst, **filter_dict)

    # If the name is unique, then return it.
    if not sub_list:
        return initial

    # Otherwise, determine how many copies of the name are in the list and
    # append a number to make this name unique.
    filter_dict = {attrib: re.escape(initial) + r'_\d+'}
    n = len(filter_list(lst, **filter_dict))
    initial = initial + '_' + str(n + 1)

    # Recursively call this routine using the newly-generated name to
    # make sure it's unique. Eventually, a unique name will be returned.
    return get_unique_name(lst, attrib, prefix, initial)


def fullmatch(regex, string, flags=0):
    """Emulate python-3.4 re.fullmatch()."""
    return re.match("(?:" + regex + r")\Z", string, flags=flags)


def filter_list(lst, **criteria):
    """
    Return a list of objects whose attributes match a set of criteria.

    Return a list of objects extracted from a list whose attributes match a
    set of criteria. The match is done using regular expressions.
    Example: filter_list(pins, name='io[0-9]+', direction='bidir') will
    return all the bidirectional pins of the component that have pin names
    starting with 'io' followed by a number (e.g., 'IO45').

    If an attribute of the lst object is a list or tuple, each entry in the
    list/tuple will be checked for a match. Only one entry needs to match to
    consider the entire attribute a match. This feature is useful when
    searching for objects that contain a list of aliases, such as Part objects.

    Args:
        lst: The list from which objects will be extracted.

    Keywords Args:
        criteria: Keyword-argument pairs. The keyword specifies the attribute
            name while the argument contains the desired value of the attribute.
            Regardless of what type the argument is, it is always compared as if
            it was a string. The argument can also be a regular expression that
            must match the entire string created from the attribute of the list
            object.

    Returns:
        A list of objects whose attributes match *all* the criteria.
    """

    def strmatch(a, b, flags):
        '''Case-insensitive string matching.'''
        return a.lower() == b.lower()

    # Determine what type of matching is needed: string or regex.
    # If no do_str_match, then do regex matching.
    # If do_str_match is False, then do regex matching.
    # If do_str_match is True, then do simple string matching.
    if criteria.pop('do_str_match', False):
        compare_func = strmatch
    else:
        compare_func = fullmatch

    # Place any matching objects from the list in here.
    extract = []

    for item in lst:
        # Compare an item's attributes to each of the criteria.
        # Break out of the criteria loop and don't add the item to the extract
        # list if *any* of the item's attributes *does not* match.
        for k, v in criteria.items():

            try:
                attr_val = getattr(item, k)
            except AttributeError:
                # If the attribute doesn't exist, then that's a non-match.
                break

            if isinstance(v, (int, basestring)):
                # Check integer or string attributes.

                if isinstance(attr_val, (list, tuple)):
                    # If the attribute value from the item is a list or tuple,
                    # loop through the list of attribute values. If at least one
                    # value matches the current criterium, then break from the
                    # criteria loop and extract this item.
                    for val in attr_val:
                        if compare_func(str(v), str(val), flags=re.IGNORECASE):
                            # One of the list of values matched, so break from this
                            # loop and do not execute the break in the
                            # loop's else clause.
                            break
                    else:
                        # If we got here, then none of the values in the attribute
                        # list matched the current criterium. Therefore, break out
                        # of the criteria loop and don't add this list item to
                        # the extract list.
                        break
                else:
                    # If the attribute value from the item in the list is a scalar,
                    # see if the value matches the current criterium. If it doesn't,
                    # then break from the criteria loop and don't extract this item.
                    if not compare_func(str(v), str(attr_val), flags=re.IGNORECASE):
                        break

            else:
                # Check non-integer, non-string attributes.
                if isinstance(attr_val, (list, tuple)):
                    if v not in attr_val:
                        break
                elif v != attr_val:
                    break

        else:
            # If we get here, then all the item attributes matched and the
            # for criteria loop didn't break, so add this item to the
            # extract list.
            extract.append(item)

    return extract


def expand_indices(slice_min, slice_max, *indices):
    """
    Expand a list of indices into a list of integers and strings.

    This function takes the indices used to select pins of parts and 
    lines of buses and returns a flat list of numbers and strings.
    String and integer indices are put in the list unchanged, but
    slices are expanded into a list of integers before entering the
    final list.

    Args:
        slice_min: The minimum possible index.
        slice_max: The maximum possible index (used for slice indices).
        indices: A list of indices made up of numbers, slices, text strings.

    Returns:
        A linear list of all the indices made up only of numbers and strings.
    """

    def expand_slice(slc):
        """Expand slice notation."""

        # Get bounds for slice.
        start, stop, step = slc.indices(slice_max)
        start = min(max(start, slice_min), slice_max)
        stop = min(max(stop, slice_min), slice_max)

        # Do this if it's a downward slice (e.g., [7:0]).
        if start > stop:
            if slc.start and slc.start > slice_max:
                logger.error('Index out of range ({} > {})!'.format(
                    slc.start, slice_max))
                raise Exception
            # Count down from start to stop.
            stop = stop - step
            step = -step

        # Do this if it's a normal (i.e., upward) slice (e.g., [0:7]).
        else:
            if slc.stop and slc.stop > slice_max:
                logger.error('Index out of range ({} > {})!'.format(
                    slc.stop, slice_max))
                raise Exception
            # Count up from start to stop
            stop += step

        # Create the sequence of indices.
        return range(start, stop, step)

    # Expand each index and add it to the list.
    ids = []
    for indx in flatten(indices):
        if isinstance(indx, slice):
            ids.extend(expand_slice(indx))
        elif isinstance(indx, int):
            ids.append(indx)
        elif isinstance(indx, basestring):
            # String might contain multiple indices with a separator.
            for id in indx.split(INDEX_SEPARATOR):
                # If the id is a valid bus expression, then the exploded bus lines
                # are added to the list of ids. If not, the original id is
                # added to the list.
                ids.extend(explode(id.strip()))
        else:
            logger.error('Unknown type in index: {}.'.format(type(indx)))
            raise Exception

    # Return the completely expanded list of indices.
    return ids


def explode(bus_str):
    """
    Explode a bus into its separate lines.

    This function takes a bus expression like "ADDR[0:3]" and returns
    "ADDR0,ADDR1,ADDR2,ADDR3". It also works if the order is reversed,
    e.g. "ADDR[3:0]" returns "ADDR3,ADDR2,ADDR1,ADDR0". If the input
    string is not a valid bus expression, then the string is returned
    in a one-element list.

    Args:
        bus_str: A string containing a bus expression like "D[0:3]".

    Returns:
        A list of bus lines like ['D0', 'D1', 'D2', 'D3'] or a one-element
        list with the original input string if it's not a valid bus expression.
    """

    bus = re.match('^([A-Za-z_]+)\[([0-9]+):([0-9]+)\]$', bus_str)
    if not bus:
        return [bus_str] # Not a valid bus expression, so return input string.
    bus_name = bus.group(1)
    begin_num = int(bus.group(2))
    end_num = int(bus.group(3))
    dir = [1, -1][int(begin_num > end_num)] # Bus indexes increasing or decreasing?
    bus_pin_nums = range(begin_num, end_num+dir, dir)
    return [bus_name+str(n) for n in bus_pin_nums]


def find_num_copies(**attribs):
    """
    Return the number of copies to based on the number of attribute values.

    Keyword Args:
        attribs: Dict of Keyword/Value pairs for setting object attributes.
            If the value is a scalar, then the number of copies is one.
            If the value is a list/tuple, the number of copies is the
            length of the list/tuple.

    Returns:
        The length of the longest value in the dict of attributes.

    Raises:
        Exception if there are two or more list/tuple values with different
        lengths that are greater than 1. (All attribute values must be scalars
        or lists/tuples of the same length.)
    """
    num_copies = set()
    for k, v in attribs.items():
        if isinstance(v, (list, tuple)):
            num_copies.add(len(v))
        else:
            num_copies.add(1)

    num_copies = list(num_copies)
    if len(num_copies) > 2:
        logger.error(
            "Mismatched lengths of attributes: {}!".format(num_copies))
        raise Exception
    elif len(num_copies) > 1 and min(num_copies) > 1:
        logger.error(
            "Mismatched lengths of attributes: {}!".format(num_copies))
        raise Exception

    try:
        return max(num_copies)
    except ValueError:
        return 0  # If the list if empty.


@contextmanager
def opened(f_or_fn, mode):
    """
    Yields an opened file or file-like object.

    Args:
       file_or_filename: Either an already opened file or file-like
           object, or a filename to open.
       mode: The mode to open the file in.
    """
    if isinstance(f_or_fn, basestring):
        with open(f_or_fn, mode) as f:
            yield f
    elif hasattr(f_or_fn, "fileno"):
        if mode.replace("+", "") == f_or_fn.mode.replace("+", ""):
            # same mode, can reuse file handle
            yield f_or_fn
        else:
            # open in new mode
            with os.fdopen(f_or_fn.fileno(), mode) as f:
                yield f
    else:
        raise TypeError(
            "argument must be a filename or a file-like object (is: {})".
            format(type(f_or_fn)))


def expand_buses(pins_nets_buses):
    """
    Take list of pins, nets, and buses and return a list of only pins and nets.
    """

    from .Bus import Bus

    pins_nets = []
    for pnb in pins_nets_buses:
        if isinstance(pnb, Bus):
            pins_nets.extend(pnb.get_nets())
        else:
            pins_nets.append(pnb)
    return pins_nets
