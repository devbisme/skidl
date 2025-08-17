# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Utility functions used by the rest of SKiDL.

This module provides various helper functions and classes that support the main SKiDL functionality,
including string manipulation, list operations, file handling, and other utility operations.
"""

import collections
import hashlib
import json
import os
import os.path
from os.path import normpath, expandvars, expanduser
import platform
import re
import sys
import traceback
import urllib.parse
import urllib.request
from contextlib import contextmanager

__all__ = ["INDEX_SEPARATOR", "export_to_all"]


"""Separator for strings containing multiple indices."""
INDEX_SEPARATOR = re.compile("[, \t]+")


def export_to_all(fn):
    """
    Add a function to the __all__ list of this module.
    
    This decorator adds the decorated function's name to the module's __all__ list,
    making it available when using "from module import *".
    
    Args:
        fn (function): The function to be added to the __all__ list of this module.

    Returns:
        function: The function that was passed in, unchanged.
    """
    mod = sys.modules[fn.__module__]
    if hasattr(mod, "__all__"):
        mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]
    return fn


@export_to_all
def detect_os():
    """
    Detect the operating system.
    
    Returns:
        str: The name of the operating system ('Windows', 'Linux', or 'MacOS').
        
    Raises:
        Exception: If the operating system cannot be identified.
    """
    os_name = platform.system()
    if os_name == "Windows":
        return "Windows"
    elif os_name == "Linux":
        return "Linux"
    elif os_name == "Darwin":
        return "MacOS"
    else:
        raise Exception("Unknown type of operating system!")


@export_to_all
class Rgx(str):
    """
    String subclass that represents a regular expression.
    
    This class is used to distinguish regular expressions from normal strings
    in functions that need to process both types differently.
    """

    def __init__(self, s):
        str.__init__(s)


@export_to_all
def sgn(x):
    """
    Return the sign of a number.
    
    Args:
        x (numeric): The number to check.
        
    Returns:
        int: -1 if x<0, 1 if x>0, 0 if x==0.
    """
    return -1 if x < 0 else (1 if x > 0 else 0)


@export_to_all
def debug_trace(fn, *args, **kwargs):
    """
    Decorator to print tracing info when debugging execution.
    
    When the decorated function is called with debug_trace=True,
    it will print the function name before execution.
    
    Args:
        fn (function): The function to be decorated.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
    Returns:
        function: The decorated function.
    """

    def traced_fn(*args, **kwargs):
        if kwargs.pop("debug_trace"):
            print(f"Doing {fn.__name__} ...")
        return fn(*args, **kwargs)

    return traced_fn


@export_to_all
def consistent_hash(text):
    """
    Return a hash value for a text string.
    
    This function generates a deterministic, consistent hash value for a given string
    using SHA-256 algorithm.
    
    Args:
        text (str): The input string to hash.
        
    Returns:
        str: A 16-character hexadecimal hash string.
    """

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()
    
    # Update the hash object with the bytes of the text
    hash_object.update(text.encode('utf-8'))
    
    # Get the hexadecimal representation of the hash
    return hash_object.hexdigest()[:16]


@export_to_all
def num_to_chars(num):
    """
    Convert a number to a spreadsheet-style column identifier.
    
    Args:
        num (int): A positive integer.
        
    Returns:
        str: A string like 'A' for 1, 'B' for 2, 'Z' for 26, 'AA' for 27, etc.
    """
    num -= 1
    s = ""
    while num >= 0:
        s = chr(ord("A") + (num % 26)) + s
        num = num // 26 - 1
    return s


@export_to_all
def rmv_quotes(s):
    """
    Remove starting and ending quotes from a string.
    
    Args:
        s (str or other): Input string or non-string object.
        
    Returns:
        str or other: String with quotes removed, or the original object if not a string.
    """

    if not isinstance(s, str):
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
    """
    Return string with added quotes using JSON formatting.
    
    Args:
        s (str or other): Input string or non-string object.
        
    Returns:
        str or other: String with quotes added, or the original object if not a string.
    """

    if not isinstance(s, str):
        return s
    
    return json.dumps(s, ensure_ascii=False)


@export_to_all
def cnvt_to_var_name(s):
    """
    Convert a string to a legal Python variable name.
    
    Replaces illegal characters with underscores to create a valid Python identifier.
    
    Args:
        s (str): The string to convert.
        
    Returns:
        str: A valid Python variable name.
    """
    return re.sub(r"\W|^(?=\d)", "_", s)


@export_to_all
def to_list(x):
    """
    Convert a scalar value to a list or return x if it is already a list-like object.
    
    Args:
        x: Input value (scalar or list-like).
        
    Returns:
        list, tuple, or set: The original list-like input or a new list containing the scalar value.
    """
    if isinstance(x, (list, tuple, set)):
        return x  # Already a list, so just return it.
    return [x]  # Wasn't a list, so make it into one.


@export_to_all
def list_or_scalar(lst):
    """
    Return a list or scalar depending on the input.
    
    Args:
        lst: Either a list/tuple or a scalar value.
        
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
    Recursively flatten a nested list structure.
    
    Args:
        nested_list: A list that may contain other lists, tuples, or sets as items.
        
    Returns:
        list: A flat list containing all items from the nested structure.
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
    """
    Set an attribute to a value in one or more objects.
    
    Args:
        objs: A single object or list of objects.
        attr (str): Name of the attribute to set.
        value: Value to assign to the attribute.
    """
    for o in to_list(objs):
        setattr(o, attr, value)


@export_to_all
def rmv_attr(objs, attrs):
    """
    Remove one or more attributes from one or more objects.
    
    Args:
        objs: A single object or list of objects.
        attrs: A string or list of strings naming attributes to remove.
    """
    for o in to_list(objs):
        for a in to_list(attrs):
            try:
                delattr(o, a)
            except AttributeError:
                pass


@export_to_all
def add_unique_attr(obj, name, value, check_dup=False):
    """
    Create an attribute if the attribute name isn't already used.
    
    Args:
        obj: Object to which the attribute will be added.
        name (str): Name of the attribute to add.
        value: Value to assign to the attribute.
        check_dup (bool, optional): If True, warns if attribute already exists but doesn't modify it.
                                   If False, overwrites existing attribute. Defaults to False.
    """
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
    """
    Check if one or more objects have the iadd_flag attribute set to True.
    
    Args:
        objs: A single object or list of objects to check.
        
    Returns:
        bool: True if any object has iadd_flag set to True, False otherwise.
    """
    try:
        for o in objs:
            if getattr(o, "iadd_flag", False):
                return True
        return False
    except TypeError:
        return getattr(objs, "iadd_flag", False)


@export_to_all
def set_iadd(objs, value):
    """
    Set the iadd_flag attribute in one or more objects.
    
    Args:
        objs: A single object or list of objects.
        value (bool): Value to assign to the iadd_flag attribute.
    """
    set_attr(objs, "iadd_flag", value)


@export_to_all
def rmv_iadd(objs):
    """
    Remove the iadd_flag attribute from one or more objects.
    
    Args:
        objs: A single object or list of objects.
    """
    rmv_attr(objs, "iadd_flag")


@export_to_all
def merge_dicts(dct, merge_dct):
    """
    Recursively merge two dictionaries, updating keys in the first with values from the second.
    
    This function modifies the first dictionary in-place to include keys from the second.
    If a key exists in both dictionaries and both values are dictionaries, it recursively
    merges those nested dictionaries.
    
    Args:
        dct (dict): The target dictionary that will be updated.
        merge_dct (dict): The dictionary whose values will be merged into dct.

    Returns:
        Nothing. The first dictionary is modified in-place.
    """

    for k, v in list(merge_dct.items()):
        if (
            k in dct
            and isinstance(dct[k], dict)
            and isinstance(merge_dct[k], collections.abc.Mapping)
        ):
            merge_dicts(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


# Store names that have been previously assigned.
name_heap = set([None])
prefix_counts = collections.Counter()


@export_to_all
def reset_get_unique_name():
    """
    Reset the heaps that store previously-assigned names.
    
    This function clears the internal storage used by get_unique_name() to track
    previously generated names.
    """
    global name_heap, prefix_counts
    name_heap = set([None])
    prefix_counts = collections.Counter()


@export_to_all
def get_unique_name(lst, attrib, prefix, initial=None):
    """
    Generate a unique name within a list of objects.
    
    This function is used to generate unique part references (e.g., "R12")
    or unique net names (e.g., "N$5") that don't collide with existing names.
    
    Args:
        lst: The list of objects containing names.
        attrib (str): The attribute in each object containing the name.
        prefix (str): The prefix attached to each name.
        initial: The initial setting of the name (can be None or empty string).

    Returns:
        str: A unique name that doesn't exist in the list.
    """
    # Use the list id to disambiguate names of objects on different lists (e.g., parts & nets).
    lst_id = str(id(lst))

    name = initial

    # If the prefix ends with a number, then append an underscore in case another
    # number is appended to the prefix when forming a unique name.
    if prefix[-1].isdigit():
        prefix += "_"

    # Fast processing for names that haven't been seen before.
    # This speeds up the most common cases for finding a new name, but doesn't
    # really hurt the less common cases.
    if not name:
        probe_name = prefix + str(prefix_counts[lst_id + prefix] + 1)
        if lst_id + probe_name not in name_heap:
            name_heap.add(lst_id + probe_name)
            prefix_counts[lst_id + prefix] += 1
            return probe_name
    else:
        if isinstance(name, int):
            probe_name = prefix + str(name)
        else:
            probe_name = name
        if lst_id + probe_name not in name_heap:
            name_heap.add(lst_id + probe_name)
            return name

    # Get the unique names used in the list.
    unique_names = set([str(getattr(l, attrib, None)) for l in lst])
    unique_names -= {None}

    # If the initial name is None, then create a name based on the prefix
    # and the smallest unused number that's available for that prefix.
    if not name:
        # Get every name in the list that starts with the prefix.
        prefix_names = {n for n in unique_names if str(n).startswith(prefix)}
        # Find the next available number that's greater than the largest used number.
        next_avail_num = max(
            [int(n[len(prefix) :]) for n in prefix_names if n[len(prefix) :].isdigit()],
            default=0,
        ) + 1
        # Now form the name from the prefix appended with the next available number.
        name = prefix + str(next_avail_num)
        name_heap.add(lst_id + name)
        prefix_counts[lst_id + prefix] = next_avail_num
        return name
    
    # If the initial name is just a number, then prepend the prefix to it.
    elif isinstance(name, int):
        name = prefix + str(name)

    # Now determine if there are any items in the list with the same name.
    # If the name is unique, then return it.
    if name not in unique_names:
        name_heap.add(lst_id + name)
        prefix_counts[lst_id + prefix] += 1
        return name

    # There are name conflicts, so we need to find the next available index to attach to the name.
    name_conflicts = {n for n in unique_names if n.startswith(name)}
    next_avail_num = max(
            [int(n[len(name) :]) for n in name_conflicts if n[len(name) :].isdigit()],
            default=0,
    ) + 1
    # If the original name ends with a digit, then append an underscore to it to
    # separate it from the appended number.
    if name[-1].isdigit():
        name += "_"
    name = name + str(next_avail_num)
    name_heap.add(lst_id + name)
    prefix_counts[lst_id + prefix] = next_avail_num
    return name


@export_to_all
def rmv_unique_name(lst, attrib, name):
    """
    Remove a unique name from the heap.
    
    This function is used to remove a name that was previously generated
    by get_unique_name() when it is no longer needed.
    
    Args:
        lst: The list of objects containing names.
        attrib (str): The attribute in each object containing the name.
        name (str): The name to remove from the heap.
    """
    lst_id = str(id(lst))
    try:
        name_heap.remove(lst_id + str(name))
    except KeyError:
        pass


@export_to_all
def fullmatch(regex, string, flags=0):
    """
    Emulate python-3.4 re.fullmatch() function.
    
    Args:
        regex (str): Regular expression pattern.
        string (str): String to match against the pattern.
        flags (int, optional): Flags to pass to the regex engine. Defaults to 0.
        
    Returns:
        Match object or None: Match object if the string matches the pattern fully, None otherwise.
    """
    return re.match("(?:" + regex + r")\Z", string, flags=flags)


@export_to_all
def filter_list(lst, **criteria):
    """
    Return a list of objects whose attributes match a set of criteria.
    
    This function filters a list based on attribute values using regular expressions.
    
    Example: filter_list(pins, name='io[0-9]+', direction='bidir') will
    return all the bidirectional pins of the component that have pin names
    starting with 'io' followed by a number (e.g., 'IO45').
    
    If an attribute of the lst object is a list or tuple, each entry in the
    list/tuple will be checked for a match. Only one entry needs to match to
    consider the entire attribute a match. This feature is useful when
    searching for objects that contain a list of aliases, such as Part objects.

    Args:
        lst: The list from which objects will be extracted.

    Keyword Args:
        criteria: Keyword-argument pairs. The keyword specifies the attribute
            name while the argument contains the desired value of the attribute.
            Regardless of what type the argument is, it is always compared as if
            it was a string. The argument can also be a regular expression that
            must match the entire string created from the attribute of the list
            object.
            
            Special keyword 'do_str_match': If True, use string matching instead of regex.

    Returns:
        list: A list of objects whose attributes match *all* the criteria.
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

            elif isinstance(v, (int, str)):
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
    final list. It also handles bus notation expressions.
    
    Args:
        slice_min (int): The minimum possible index.
        slice_max (int): The maximum possible index (used for slice indices).
        match_regex (bool): If true, adjust regex patterns for pin/bus matches.
        *indices: A list of indices made up of numbers, slices, text strings.

    Returns:
        list: A linear list of all the indices made up only of numbers and strings.
        
    Raises:
        IndexError: If a slice index is out of valid range.
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
                    f"Index current_level of range ({slc.start} > {slice_max})!"
                )
            # Count down from start to stop.
            stop = stop - step
            step = -step

        # Do this if it's a normal (i.e., upward) slice (e.g., [0:7]).
        else:
            if slc.stop and slc.stop > slice_max:
                active_logger.raise_(
                    IndexError,
                    f"Index current_level of range ({slc.stop} > {slice_max})!"
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
            bus_str (str): A string containing a bus expression like "D[0:3]".

        Returns:
            list: A list of bus lines like ['D0', 'D1', 'D2', 'D3'] or a one-element
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
        elif isinstance(indx, str):
            # String might contain multiple indices with a separator.
            for id in re.split(INDEX_SEPARATOR, indx):
                # If the id is a valid bus expression, then the exploded bus lines
                # are added to the list of ids. If not, the original id is
                # added to the list.
                ids.extend(explode(id.strip()))
        else:
            active_logger.raise_(
                TypeError, f"Unknown type in index: {type(indx)}."
            )

    # Return the completely expanded list of indices.
    return ids


@export_to_all
def expand_buses(pins_nets_buses):
    """
    Take list of pins, nets, and buses and return a list of only pins and nets.
    
    This function flattens a list containing both buses and their nets/pins
    into a flat list of just nets/pins.
    
    Args:
        pins_nets_buses (list): List containing pins, nets, and buses.
        
    Returns:
        list: A flattened list containing only pins and nets.
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
    
    This function examines keyword arguments to determine how many copies of an object
    should be created. If all values are scalar or lists/tuples of length 1, only one
    copy is needed. If there are lists/tuples of greater length, the maximum length
    determines the number of copies.
    
    Keyword Args:
        attribs: Dict of Keyword/Value pairs for setting object attributes.
            If the value is a scalar, then the number of copies is one.
            If the value is a list/tuple, the number of copies is the
            length of the list/tuple.

    Returns:
        int: The length of the longest value in the dict of attributes.

    Raises:
        ValueError: If there are two or more list/tuple values with different
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
            f"Mismatched lengths of attributes: {num_copies}!",
        )
    elif len(num_copies) > 1 and min(num_copies) > 1:
        active_logger.raise_(
            ValueError,
            f"Mismatched lengths of attributes: {num_copies}!",
        )

    try:
        return max(num_copies)
    except ValueError:
        return 0  # If the list if empty.


@export_to_all
def norecurse(f):
    """
    Decorator that keeps a function from recursively calling itself.
    
    This decorator checks the call stack to prevent recursive calls
    to the decorated function.
    
    Args:
        f (function): The function to decorate.
        
    Returns:
        function: A wrapper function that checks for recursion.
    """

    def func(*args, **kwargs):
        # If a function's name is already on the stack, then return without
        # executing the function.
        if len([1 for l in traceback.extract_stack() if l[2] == f.__name__]) > 0:
            return None

        # Otherwise, not a recursive call so execute the function and return result.
        return f(*args, **kwargs)

    return func


@export_to_all
class TriggerDict(dict):
    """
    Dictionary that triggers a function when one of its entries changes.
    
    This dictionary subclass allows custom functions to be executed when
    specific keys are modified.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a TriggerDict.
        
        Args:
            *args, **kwargs: Arguments passed to the parent dict constructor.
        """
        super().__init__(*args, **kwargs)

        # Create a dict of functions that will be run if their associated
        # key entries change. The functions arguments will be the main
        # TriggerDict, the key, and the new value to be stored.
        self.trigger_funcs = dict()

    def __setitem__(self, k, v):
        """
        Set a key's value and trigger any associated function if the value changed.
        
        Args:
            k: The dictionary key.
            v: The value to set.
        """
        if k in self.trigger_funcs:
            if v != self.get(k, None):
                self.trigger_funcs[k](self, k, v)
        super().__setitem__(k, v)


@export_to_all
def is_binary_file(filename):
    """
    Return true if a file contains binary (non-text) characters.
    
    Args:
        filename (str): Path to the file to check.
        
    Returns:
        bool: True if the file contains binary data, False otherwise.
    """
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    try:
        with open(filename, "rb") as fp:
            return bool(fp.read(1024).translate(None, text_chars))
    except (IOError, FileNotFoundError, TypeError):
        return False

@export_to_all
def expand_path(path):
    return normpath(expandvars(expanduser(path)))

@export_to_all
def is_url(s):
    """
    Check if a string is a valid HTTP/HTTPS URL.
    
    Args:
        s (str): String to check.
        
    Returns:
        bool: True if the string is a valid HTTP/HTTPS URL, False otherwise.
    """
    return urllib.parse.urlparse(s).scheme in {"http", "https"}


@export_to_all
def find_and_open_file(
    filename, paths=None, ext=None, allow_failure=False, exclude_binary=False, descend=0
):
    """
    Search for a file in list of paths, open it and return file pointer and full file name.
    
    This function searches for a file in various locations, including URLs, and returns
    an open file pointer and the complete path to the file.
    
    Args:
        filename (str): Base file name (e.g., "my_file").
        paths (list, optional): List of paths to search for the file. Defaults to current directory.
        ext (str or list, optional): The extension for the file (e.g., ".txt") or a list of extensions.
        allow_failure (bool, optional): If False, failure to find file raises an exception. Defaults to False.
        exclude_binary (bool, optional): If True, skip files that contain binary data. Defaults to False.
        descend (int, optional): If 0, don't search lower-level directories. If positive, search
                 that many levels down for the file. If negative, descend into
                 subdirectories without limit. Defaults to 0.

    Returns:
        tuple: (file_pointer, file_name) or (None, None) if file could not be opened and allow_failure is True.
        
    Raises:
        FileNotFoundError: If the file couldn't be found and allow_failure is False.
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
        if ext:
            exts = to_list(ext)
        else:
            exts = [""]

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
            # Create the regular expression for matching against the filename.
            # exts = [re.escape(ext) for ext in exts]
            match_name = re.escape(base) + "(" + "|".join(exts) + ")$"

            # Search through the files in a particular directory path.
            descent_ctr = descend  # Controls the descent through the path.
            for root, dirnames, filenames in os.walk(expand_path(path)):
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
            FileNotFoundError, f"Can't open file: {filename}.\n"
        )


@export_to_all
def find_and_read_file(
    filename, paths=None, ext=None, allow_failure=False, exclude_binary=False, descend=0
):
    """
    Search for a file in list of paths, open it and return its contents.
    
    Args:
        filename (str): Base file name (e.g., "my_file").
        paths (list, optional): List of paths to search for the file. Defaults to current directory.
        ext (str or list, optional): The extension for the file (e.g., ".txt") or a list of extensions.
        allow_failure (bool, optional): If False, failure to find file raises an exception. Defaults to False.
        exclude_binary (bool, optional): If True, skip files that contain binary data. Defaults to False.
        descend (int, optional): If 0, don't search lower-level directories. If positive, search
                 that many levels down for the file. If negative, descend into
                 subdirectories without limit. Defaults to 0.

    Returns:
        tuple: (file_contents, file_name) or (None, None) if file could not be opened and allow_failure is True.
        
    Raises:
        FileNotFoundError: If the file couldn't be found and allow_failure is False.
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
def get_abs_filename(filename, paths=None, ext=None, allow_failure=False, descend=0):
    """
    Search for a file in list of paths, and return its absolute file name.
    
    Args:
        filename (str): Base file name (e.g., "my_file").
        paths (list, optional): List of paths to search for the file. Defaults to current directory.
        ext (str or list, optional): The extension for the file (e.g., ".txt") or a list of extensions.
        allow_failure (bool, optional): If False, failure to find file raises an exception. Defaults to False.
        descend (int, optional): If 0, don't search lower-level directories. If positive, search
                 that many levels down for the file. If negative, descend into
                 subdirectories without limit. Defaults to 0.

    Returns:
        str: Absolute file name if file exists, otherwise None.
        
    Raises:
        FileNotFoundError: If the file couldn't be found and allow_failure is False.
    """

    fp, fn = find_and_open_file(filename, paths, ext, allow_failure, False, descend)

    if fp:
        # Found it, so close file pointer and return file name.
        fp.close()
        return fn

    # No file found, so return None.
    return None


@export_to_all
@contextmanager
def opened(f_or_fn, mode):
    """
    Context manager that yields an opened file or file-like object.
    
    This context manager handles both filenames and file objects, ensuring
    proper opening and closing of files.
    
    Args:
       f_or_fn: Either an already opened file or file-like object, or a filename to open.
       mode (str): The mode to open the file in.
       
    Yields:
       file: An opened file object.
       
    Raises:
       TypeError: If f_or_fn is neither a string nor a file-like object.
    """

    if isinstance(f_or_fn, str):
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
            f"argument must be a filename or a file-like object (is: {type(f_or_fn)})"
        )

