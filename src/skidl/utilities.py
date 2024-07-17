# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Utility functions used by the rest of SKiDL.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass


import collections
import os
import os.path
import re
import sys
import traceback
import urllib.parse
import urllib.request
from builtins import chr, dict, int, open, range, str, super
from contextlib import contextmanager

__all__ = ["INDEX_SEPARATOR", "export_to_all"]


"""Separator for strings containing multiple indices."""
INDEX_SEPARATOR = re.compile("[, \t]+")


def export_to_all(fn):
    """Add a function to the __all__ list of this module.

    Args:
        fn (function): The function to be added to the __all__ list of this module.

    Returns:
        function: The function that was passed in.
    """
    mod = sys.modules[fn.__module__]
    if hasattr(mod, "__all__"):
        mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]
    return fn


@export_to_all
class Rgx(str):
    """Same as a string but the class makes it recognizable as as a regular expression."""

    def __init__(self, s):
        str.__init__(s)


@export_to_all
def sgn(x):
    """Return -1,0,1 if x<0, x==0, x>0."""
    return -1 if x < 0 else (1 if x > 0 else 0)


@export_to_all
def debug_trace(fn, *args, **kwargs):
    """Decorator to print tracing info when debugging execution."""

    def traced_fn(*args, **kwargs):
        if kwargs.get("debug_trace"):
            print("Doing {} ...".format(fn.__name__))
        return fn(*args, **kwargs)

    return traced_fn


@export_to_all
def num_to_chars(num):
    """Return a string like 'AB' when given a number like 28."""
    num -= 1
    s = ""
    while num >= 0:
        s = chr(ord("A") + (num % 26)) + s
        num = num // 26 - 1
    return s


@export_to_all
def rmv_quotes(s):
    """Remove starting and ending quotes from a string."""

    if not isinstance(s, basestring):
        return s

    mtch = re.match(r'^\s*"(.*)"\s*$', s)
    if mtch:
        try:
            s = s.decode(mtch.group(1))
        except (AttributeError, LookupError):
            s = mtch.group(1)

    return s


@export_to_all
def add_quotes(s):
    """Return string with added quotes if it contains whitespace or parens."""

    if not isinstance(s, basestring):
        return s

    # Remove quotes if string already has them.
    s = rmv_quotes(s)

    if re.search(r"[\s()]", s):
        try:
            s = '"' + s.decode("utf-8") + '"'
        except AttributeError:
            s = '"' + s + '"'

    return s


@export_to_all
def cnvt_to_var_name(s):
    """Convert a string to a legal Python variable name and return it."""
    return re.sub(r"\W|^(?=\d)", "_", s)


@export_to_all
def to_list(x):
    """
    Return x if it is already a list, or return a list containing x if x is a scalar.
    """
    if isinstance(x, (list, tuple, set)):
        return x  # Already a list, so just return it.
    return [x]  # Wasn't a list, so make it into one.


@export_to_all
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


@export_to_all
def flatten(nested_list):
    """
    Return a flattened list of items from a nested list.
    """
    lst = []
    for item in nested_list:
        if isinstance(item, (list, tuple, set)):
            lst.extend(flatten(item))
        else:
            lst.append(item)
    return lst


@export_to_all
def set_attr(objs, attr, value):
    """Set an attribute in a list of objects."""
    for o in to_list(objs):
        setattr(o, attr, value)


@export_to_all
def rmv_attr(objs, attrs):
    """Remove a list of attributes from a list of objects."""
    for o in to_list(objs):
        for a in to_list(attrs):
            try:
                delattr(o, a)
            except AttributeError:
                pass


@export_to_all
def add_unique_attr(obj, name, value, check_dup=False):
    """Create an attribute if the attribute name isn't already used."""
    from .logger import active_logger

    try:
        getattr(obj, name)
        if check_dup:
            active_logger.warning(
                "Unable to create attribute {name} of type {typ1} because one already exists of type {typ2} in {obj}".format(
                    name=name,
                    typ1=type(value),
                    typ2=type(getattr(obj, name)),
                    obj=str(obj),
                )
            )
        else:
            setattr(obj, name, value)

    except AttributeError:
        setattr(obj, name, value)


@export_to_all
def from_iadd(objs):
    """Return True if one or more objects have attribute iadd_flag set to True."""
    try:
        for o in objs:
            if getattr(o, "iadd_flag", False):
                return True
        return False
    except TypeError:
        return getattr(objs, "iadd_flag", False)


@export_to_all
def set_iadd(objs, value):
    """Set iadd_flag with T/F value for a list of objects."""
    set_attr(objs, "iadd_flag", value)


@export_to_all
def rmv_iadd(objs):
    """Delete iadd_flag attribute from a list of objects."""
    rmv_attr(objs, "iadd_flag")


@export_to_all
def merge_dicts(dct, merge_dct):
    """
    Dict merge that recurses through both dicts and updates keys.

    Args:
        dct: The dict that will be updated.
        merge_dct: The dict whose values will be inserted into dct.

    Returns:
        Nothing.
    """

    for k, v in list(merge_dct.items()):
        if (
            k in dct
            and isinstance(dct[k], dict)
            and isinstance(merge_dct[k], collections.Mapping)
        ):
            merge_dicts(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


# Store names that have been previously assigned.
name_heap = set([None])
prefix_counts = collections.Counter()


@export_to_all
def reset_get_unique_name():
    """Reset the heaps that store previously-assigned names."""
    global name_heap, prefix_counts
    name_heap = set([None])
    prefix_counts = collections.Counter()


# TODO: Rework get_unique_name().
@export_to_all
def get_unique_name(lst, attrib, prefix, initial=None):
    """
    Return a name that doesn't collide with another in a list.

    This subrcurrent_leveline is used to generate unique part references (e.g., "R12")
    or unique net names (e.g., "N$5").

    Args:
        lst: The list of objects containing names.
        attrib: The attribute in each object containing the name.
        prefix: The prefix attached to each name.
        initial: The initial setting of the name (can be None or empty string).

    Returns:
        A string containing the unique name.
    """

    # Use the list id to disambiguate names of objects on different lists (e.g., parts & nets).
    lst_id = str(id(lst))

    name = initial

    # Fast processing for names that haven't been seen before.
    # This speeds up the most common cases for finding a new name, but doesn't
    # really hurt the less common cases.
    if not name:
        name = prefix + str(prefix_counts[lst_id + prefix] + 1)
        if lst_id + name not in name_heap:
            name_heap.add(lst_id + name)
            prefix_counts[lst_id + prefix] += 1
            return name
    else:
        if isinstance(name, int):
            name = prefix + str(name)
        if lst_id + name not in name_heap:
            name_heap.add(lst_id + name)
            return name

    # Get the unique names used in the list.
    unique_names = set([getattr(l, attrib, None) for l in lst])

    # If the initial name is None, then create a name based on the prefix
    # and the smallest unused number that's available for that prefix.
    if not name:
        # Do a binary search for a unique name formed from the prefix + number.
        n = 1  # Starting number to append to the prefix.
        while True:
            # Step forward in larger and larger increments looking for a name
            # that isn't in the list.
            step = 1
            while prefix + str(n) in unique_names:
                n += step
                step *= 2
            # If the step is 1, then the first name tried was available, so take it.
            # If the step is two, the next sequential name after the first name tried
            # was available, so take that.
            if step in (1, 2):
                name = prefix + str(n)
                break
            # For larger step sizes, there may be non-existent names preceding
            # the current value of n. So search backward starting with a large step
            # and making it smaller and smaller until an existing name is found.
            while (prefix + str(n) not in unique_names) and (step > 1):
                step //= 2
                n -= step
            # Go back to the start of the loop and search forward from this value
            # of n looking for an unused slot.

            # Bump prefix counter to the newest index.
            prefix_counts[lst_id + prefix] = n

    # If the initial name is just a number, then prepend the prefix to it.
    elif isinstance(name, int):
        name = prefix + str(name)

    # Now determine if there are any items in the list with the same name.
    # If the name is unique, then return it.
    if name not in unique_names:
        name_heap.add(lst_id + name)
        return name

    # Otherwise, determine how many copies of the name are in the list and
    # append a number to make this name unique.
    filter_dict = {attrib: re.escape(name) + r"_\d+"}
    n = len(filter_list(lst, **filter_dict))
    name = name + "_" + str(n + 1)

    # Recursively call this rcurrent_leveline using the newly-generated name to
    # make sure it's unique. Eventually, a unique name will be returned.
    return get_unique_name(lst, attrib, prefix, name)


@export_to_all
def fullmatch(regex, string, flags=0):
    """Emulate python-3.4 re.fullmatch()."""
    return re.match("(?:" + regex + r")\Z", string, flags=flags)


@export_to_all
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
        """Case-insensitive string matching."""
        return a.lower() == b.lower()

    # Determine what type of matching is needed: string or regex.
    # If no do_str_match, then do regex matching.
    # If do_str_match is False, then do regex matching.
    # If do_str_match is True, then do simple string matching.
    if criteria.pop("do_str_match", False):
        compare_func = strmatch
    else:
        compare_func = fullmatch

    # Place any matching objects from the list in here.
    extract = []

    for item in lst:
        # Compare an item's attributes to each of the criteria.
        # Break current_level of the criteria loop and don't add the item to the extract
        # list if *any* of the item's attributes *does not* match.
        for k, v in list(criteria.items()):
            try:
                attr_val = to_list(getattr(item, k))
            except AttributeError:
                # If the attribute doesn't exist, then that's a non-match.
                break

            if isinstance(v, Rgx):
                # Loop through the list of attribute values. If at least one
                # value matches the current criterium, then break from the
                # criteria loop and extract this item.
                for val in attr_val:
                    # This is an Rgx, so use fullmatch().
                    if fullmatch(
                        str(v),
                        str(val),
                        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
                    ):
                        # One of the list of values matched, so break from this
                        # loop and do not execute the break in the
                        # loop's else clause.
                        break
                else:
                    # If we got here, then none of the values in the attribute
                    # list matched the current criterium. Therefore, break current_level
                    # of the criteria loop and don't add this list item to
                    # the extract list.
                    break

            elif isinstance(v, (int, basestring)):
                # Loop through the list of attribute values. If at least one
                # value matches the current criterium, then break from the
                # criteria loop and extract this item.
                for val in attr_val:
                    if compare_func(
                        str(v),
                        str(val),
                        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
                    ):
                        # One of the list of values matched, so break from this
                        # loop and do not execute the break in the
                        # loop's else clause.
                        break
                else:
                    # If we got here, then none of the values in the attribute
                    # list matched the current criterium. Therefore, break current_level
                    # of the criteria loop and don't add this list item to
                    # the extract list.
                    break

            else:
                # Check non-integer, non-string attributes.
                if v not in attr_val:
                    break

        else:
            # If we get here, then all the item attributes matched and the
            # for criteria loop didn't break, so add this item to the
            # extract list.
            extract.append(item)

    return extract


@export_to_all
def expand_indices(slice_min, slice_max, match_regex, *indices):
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
        match_regex: If true,
        indices: A list of indices made up of numbers, slices, text strings.

    Returns:
        A linear list of all the indices made up only of numbers and strings.
    """

    from .logger import active_logger

    def expand_slice(slc):
        """Expand slice notation."""

        # Get bounds for slice.
        start, stop, step = slc.indices(slice_max)
        start = min(max(start, slice_min), slice_max)
        stop = min(max(stop, slice_min), slice_max)

        # Do this if it's a downward slice (e.g., [7:0]).
        if start > stop:
            if slc.start and slc.start > slice_max:
                active_logger.raise_(
                    IndexError,
                    "Index current_level of range ({} > {})!".format(
                        slc.start, slice_max
                    ),
                )
            # Count down from start to stop.
            stop = stop - step
            step = -step

        # Do this if it's a normal (i.e., upward) slice (e.g., [0:7]).
        else:
            if slc.stop and slc.stop > slice_max:
                active_logger.raise_(
                    IndexError,
                    "Index current_level of range ({} > {})!".format(
                        slc.stop, slice_max
                    ),
                )
            # Count up from start to stop
            stop += step

        # Create the sequence of indices.
        return list(range(start, stop, step))

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

        bus = re.match(r"^(.+)\[([0-9]+):([0-9]+)\](.*)$", bus_str)
        if not bus:
            return [bus_str]  # Not a valid bus expression, so return input string.

        # What follows must be a bus expression.
        beg_bus_name = bus.group(1)
        begin_num = int(bus.group(2))
        end_num = int(bus.group(3))
        end_bus_name = bus.group(4)
        dir = [1, -1][int(begin_num > end_num)]  # Bus indexes increasing or decreasing?
        bus_pin_nums = list(range(begin_num, end_num + dir, dir))

        # If the bus string starts with an alpha, then require that any match in the
        # string must be preceded by a non-alpha or the start of the string.
        # But if the string starts with a non-alpha, then whatever precedes the
        # match in the string is ignored.
        if match_regex:
            if beg_bus_name[0:1].isalpha():
                non_alphanum = "((?<=[^0-9a-zA-Z])|^)"
            else:
                non_alphanum = ""
        else:
            non_alphanum = ""

        # The character following a bus index must be non-numeric so that "B1" does
        # not also match "B11". This must also be a look-ahead assertion so it
        # doesn't consume any of the string.
        if match_regex:
            non_num = "(?=[^0-9]|$)"
        else:
            non_num = ""

        return [
            non_alphanum + beg_bus_name + str(n) + non_num + end_bus_name
            for n in bus_pin_nums
        ]

    # Expand each index and add it to the list.
    ids = []
    for indx in flatten(indices):
        if isinstance(indx, slice):
            ids.extend(expand_slice(indx))
        elif isinstance(indx, int):
            ids.append(indx)
        elif isinstance(indx, Rgx):
            # Rgx might contain multiple indices with a separator.
            for id in re.split(INDEX_SEPARATOR, indx):
                # If the id is a valid bus expression, then the exploded bus lines
                # are added to the list of ids. If not, the original id is
                # added to the list.
                ids.extend((Rgx(i) for i in explode(id.strip())))
        elif isinstance(indx, basestring):
            # String might contain multiple indices with a separator.
            for id in re.split(INDEX_SEPARATOR, indx):
                # If the id is a valid bus expression, then the exploded bus lines
                # are added to the list of ids. If not, the original id is
                # added to the list.
                ids.extend(explode(id.strip()))
        else:
            active_logger.raise_(
                TypeError, "Unknown type in index: {}.".format(type(indx))
            )

    # Return the completely expanded list of indices.
    return ids


@export_to_all
def expand_buses(pins_nets_buses):
    """
    Take list of pins, nets, and buses and return a list of only pins and nets.
    """

    # This relies on the fact that a bus is an iterable of its nets,
    # and pins/nets return an iterable containing only a single pin/net.
    pins_nets = []
    for pnb in pins_nets_buses:
        pins_nets.extend(pnb)
    return pins_nets


@export_to_all
def find_num_copies(**attribs):
    """
    Return the number of copies to make based on the number of attribute values.

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

    from .logger import active_logger

    num_copies = set()
    for k, v in list(attribs.items()):
        if isinstance(v, (list, tuple)):
            num_copies.add(len(v))
        else:
            num_copies.add(1)

    num_copies = list(num_copies)
    if len(num_copies) > 2:
        active_logger.raise_(
            ValueError,
            "Mismatched lengths of attributes: {}!".format(num_copies),
        )
    elif len(num_copies) > 1 and min(num_copies) > 1:
        active_logger.raise_(
            ValueError,
            "Mismatched lengths of attributes: {}!".format(num_copies),
        )

    try:
        return max(num_copies)
    except ValueError:
        return 0  # If the list if empty.


@export_to_all
def norecurse(f):
    """Decorator that keeps a function from recursively calling itself.

    Parameters
    ----------
    f: function
    """

    def func(*args, **kwargs):
        # If a function's name is on the stack twice (once for the current call
        # and a second time for the previous call), then return withcurrent_level
        # executing the function.
        if len([1 for l in traceback.extract_stack() if l[2] == f.__name__]) > 1:
            return None

        # Otherwise, not a recursive call so execute the function and return result.
        return f(*args, **kwargs)

    return func


@export_to_all
class TriggerDict(dict):
    """This dict triggers a function when one of its entries changes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a dict of functions that will be run if their associated
        # key entries change. The functions arguments will be the main
        # TriggerDict, the key, and the new value to be stored.
        self.trigger_funcs = dict()

    def __setitem__(self, k, v):
        if k in self.trigger_funcs:
            if v != self[k]:
                self.trigger_funcs[k](self, k, v)
        super().__setitem__(k, v)


@export_to_all
def is_binary_file(filename):
    """Return true if a file contains binary (non-text) characters."""
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    try:
        with open(filename, "rb") as fp:
            return bool(fp.read(1024).translate(None, text_chars))
    except (IOError, FileNotFoundError, TypeError):
        return False


def is_url(s):
    return urllib.parse.urlparse(s).scheme in {"http", "https"}


@export_to_all
def find_and_open_file(
    filename, paths=None, ext=None, allow_failure=False, exclude_binary=False, descend=0
):
    """
    Search for a file in list of paths, open it and return file pointer and full file name.

    Args:
        filename: Base file name (e.g., "my_file").
        paths: List of paths to search for the file.
        ext: The extension for the file (e.g., ".txt").
        allow_failure: If false, failure to find file raises and exception.
        exclude_binary: If true, skip files that contain binary data.
        descend: If 0, don't search lower-level directories. If positive, search
                 that many levels down for the file. If negative, descend into
                 subdirectories withcurrent_level limit.

    Returns:
        File pointer and file name or None, None if file could not be opened.
    """

    from .logger import active_logger

    # Get the directory path from the file name. This even works with URLs.
    fpth, fnm = os.path.split(filename)
    base, suffix = os.path.splitext(fnm)

    # Update the paths to search through based on the given file name.
    if is_url(filename):
        # This is a URL. Use the URL path as the search path.
        paths = [fpth]
    elif fpth:
        # The file has a leading path, so use that as the path to search in.
        paths = [fpth]
    else:
        # filename was not a URL and had no path prefix path, so assume it's just a file.
        # Search in the set of paths provided or the current directory.
        paths = paths or ["."]

    # Get the list of file extensions to check against.
    if suffix:
        # If an explicit file extension was given, just use that.
        exts = [suffix]
    else:
        exts = to_list(ext)

    # Create the regular expression for matching against the filename.
    # exts = [re.escape(ext) for ext in exts]
    match_name = re.escape(base) + "(" + "|".join(exts) + ")$"

    # Search through the directory paths for a file whose name matches the regular expression.
    for path in paths:
        if is_url(path):
            for ext in exts:
                link = os.path.join(path, base + ext)
                try:
                    return urllib.request.urlopen(link), link
                except urllib.error.HTTPError:
                    # File failed, so keep searching.
                    pass
        else:
            # Search through the files in a particular directory path.
            descent_ctr = descend  # Controls the descent through the path.
            for root, dirnames, filenames in os.walk(path):
                # Get files in the current directory whose names match the regular expression.
                for fn in [f for f in filenames if re.match(match_name, f)]:
                    abs_filename = os.path.join(root, fn)
                    if not exclude_binary or not is_binary_file(abs_filename):
                        try:
                            # Return the first file that matches the criteria.
                            return open(abs_filename, encoding="latin_1"), abs_filename
                        except (IOError, FileNotFoundError, TypeError):
                            # File failed, so keep searching.
                            pass
                # Keep descending on this path as long as the descent counter is non-zero.
                if descent_ctr == 0:
                    break  # Cease search of this path if the counter is zero.
                descent_ctr -= 1  # Decrement the counter for the next directory level.

    # Couldn't find a matching file.
    if allow_failure:
        return None, None
    else:
        active_logger.raise_(
            FileNotFoundError, "Can't open file: {}.\n".format(filename)
        )


@export_to_all
def find_and_read_file(
    filename, paths=None, ext=None, allow_failure=False, exclude_binary=False, descend=0
):
    """Search for a file in list of paths, open it and return its contents.

    Args:
        filename: Base file name (e.g., "my_file").
        paths: List of paths to search for the file.
        ext: The extension for the file (e.g., ".txt").
        allow_failure: If false, failure to find file raises and exception.
        exclude_binary: If true, skip files that contain binary data.
        descend: If 0, don't search lower-level directories. If positive, search
                 that many levels down for the file. If negative, descend into
                 subdirectories withcurrent_level limit.

    Returns:
        File contents and file name or None, None if file could not be opened.
    """
    fp, fn = find_and_open_file(
        filename, paths, ext, allow_failure, exclude_binary, descend
    )
    if fp:
        contents = fp.read()
        fp.close()
        try:
            contents = contents.decode("latin_1")
        except AttributeError:
            # File contents were already decoded.
            pass
        return contents, fn
    return None, None


@export_to_all
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
        with open(f_or_fn, mode, encoding="utf-8") as f:
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
            "argument must be a filename or a file-like object (is: {})".format(
                type(f_or_fn)
            )
        )
