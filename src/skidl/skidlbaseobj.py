# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Base object for Circuit, Interface, Part, Net, Bus, Pin objects.

This module provides the foundation class SkidlBaseObject that all major SKiDL objects
inherit from. It implements common functionality such as ERC checking, attribute handling,
and object copying.
"""

import inspect
import random
import string
import os.path
from collections import namedtuple
from copy import deepcopy

from .alias import Alias
from .note import Note
from .utilities import export_to_all


__all__ = ["OK", "WARNING", "ERROR", "HIER_SEP"]

OK, WARNING, ERROR = list(range(3))

HIER_SEP = "."  # Separator for hierarchical names.


@export_to_all
class SkidlBaseObject(object):
    """
    Base class for all SKiDL objects.

    This class provides common functionality for all SKiDL objects such as
    attribute handling, ERC checking, and object copying. It also manages
    object names, aliases, and notes.
    """

    # These are fallback lists so every object will have them to reference.
    erc_list = list()
    erc_assertion_list = list()

    def __init__(self):
        """Initialize a new SkidlBaseObject with empty fields dictionary."""
        self.fields = {}

    def __getattr__(self, key):
        """
        Retrieve an attribute from the fields dictionary.

        Args:
            key: The attribute name to retrieve.

        Returns:
            The value of the attribute.

        Raises:
            AttributeError: If the attribute doesn't exist.
        """
        try:
            # Don't use super()!! It leads to long run times on Python 2.7.
            return self.__getattribute__("fields")[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        """
        Set an attribute either directly or in the fields dictionary.

        If the key is 'fields' or doesn't exist in fields, sets it directly,
        otherwise updates the fields dictionary.

        Args:
            key: The attribute name to set.
            value: The value to assign to the attribute.
        """
        if key == "fields" or key not in self.fields:
            super().__setattr__(key, value)
        else:
            self.fields[key] = value

    def copy(self):
        """
        Create a deep copy of this object.

        Returns:
            A new SkidlBaseObject with copies of this object's fields, aliases, and notes.
        """
        cpy = SkidlBaseObject()
        cpy.fields = deepcopy(self.fields)
        try:
            cpy.aliases = deepcopy(self.aliases)
        except AttributeError:
            pass
        try:
            cpy.notes = deepcopy(self.notes)
        except AttributeError:
            pass
        return cpy

    def ERC(self, *args, **kwargs):
        """
        Run Electrical Rules Check on this object.

        This method runs all ERC functions and evaluates all ERC assertions
        assigned to the object.

        Args:
            *args: Arguments to pass to ERC functions.
            **kwargs: Keyword arguments to pass to ERC functions.
        """
        # Run ERC functions.
        self._exec_erc_functions(*args, **kwargs)

        # Run ERC assertions.
        self._eval_erc_assertions()

    def add_erc_function(self, func):
        """
        Add an ERC function to this object or its class.

        Args:
            func: A function that will be called during ERC checking.
        """
        self.erc_list.append(func)

    def add_erc_assertion(self, assertion, fail_msg="FAILED", severity=ERROR):
        """
        Add an ERC assertion to this object or its class.

        Args:
            assertion: A string containing a Python expression that should evaluate to True.
            fail_msg: Message to display if assertion fails.
            severity: Level of severity (ERROR, WARNING, or OK) if assertion fails.
        """
        # Tuple for storing assertion code object with its global & local dicts.
        EvalTuple = namedtuple(
            "EvalTuple",
            "stmnt fail_msg severity filename lineno function globals locals",
        )

        assertion_frame, filename, lineno, function, _, _ = inspect.stack()[1]
        self.erc_assertion_list.append(
            EvalTuple(
                assertion,
                fail_msg,
                severity,
                filename,
                lineno,
                function,
                assertion_frame.f_globals,
                assertion_frame.f_locals,
            )
        )

    def _eval_erc_assertions(self):
        """
        Evaluate all ERC assertions for this object.

        This method evaluates all assertions and logs failures with appropriate
        severity levels.
        """
        from .logger import active_logger

        def erc_report(evtpl):
            log_msg = "{evtpl.stmnt} {evtpl.fail_msg} in {evtpl.filename}:{evtpl.lineno}:{evtpl.function}."
            if evtpl.severity == ERROR:
                active_logger.error(log_msg)
            elif evtpl.severity == WARNING:
                active_logger.warning(log_msg)

        for evtpl in self.erc_assertion_list:
            if eval(evtpl.stmnt, evtpl.globals, evtpl.locals) == False:
                erc_report(evtpl)

    def _exec_erc_functions(self, *args, **kwargs):
        """
        Execute ERC functions on this object.

        Args:
            *args: Arbitrary argument list passed to each ERC function.
            **kwargs: Arbitrary keyword arguments passed to each ERC function.
        """
        # Execute any instance functions for this particular instance.
        for f in self.erc_list:
            f(self, *args, **kwargs)

    @property
    def name(self):
        """
        Get the primary name of this object.

        Returns:
            The primary name of this object.
        """
        return self._name

    @name.setter
    def name(self, nm):
        """
        Set the primary name of this object and add it to aliases.

        Args:
            nm: The new name for this object.
        """
        del self.name  # Remove any pre-existing name.
        self.aliases += nm
        self._name = nm

    @name.deleter
    def name(self):
        """Remove the primary name from this object and its aliases."""
        try:
            self.aliases.discard(self._name)
            self._name = None
        except AttributeError:
            pass

    @property
    def tag(self):
        """
        Get the tag of this object.

        Returns:
            The tag of this object.
        """
        return self._tag

    @tag.setter
    def tag(self, tag_):
        """
        Set the tag of this object.

        Args:
            tag_: The new tag for this object.
        """
        del self.tag  # Remove any pre-existing tag.
        self._tag = tag_

    @tag.deleter
    def tag(self):
        """Remove the tag from this object."""
        try:
            del self._tag
        except AttributeError:
            pass

    def check_tag(self, create_if_missing=False):
        """
        Check if the tag is set for this object.
        Warn if the tag is not set.

        Returns:
            True if the tag is set, False otherwise.
        """
        from skidl.logger import active_logger

        if getattr(self, "tag", None):
            return True
        else:
            active_logger.bare_warning(
                f"Missing tag on {self.name} instantiated at {self.src_line(True)}."
            )
            if create_if_missing:
                # Create a random tag if it is missing.
                chars = string.ascii_letters + string.digits + "_"
                length = 10
                self.tag = ''.join(random.choices(chars, k=length))
                active_logger.bare_warning(
                    f"Random tag {self.tag} generated for {self.name}."
                )
            return False

    @property
    def aliases(self):
        """
        Get the aliases for this object.

        Returns:
            An Alias object containing all alternate names for this object.
        """
        try:
            return self._aliases
        except AttributeError:
            return Alias([])  # No aliases, so just return an empty list.

    @aliases.setter
    def aliases(self, name_or_list):
        """
        Set aliases for this object.

        Args:
            name_or_list: A name or list of names to use as aliases.
        """
        if not name_or_list:
            return
        self._aliases = Alias(name_or_list)

    @aliases.deleter
    def aliases(self):
        """Remove all aliases from this object."""
        try:
            del self._aliases
        except AttributeError:
            pass

    @property
    def notes(self):
        """
        Get the notes for this object.

        Returns:
            A Note object containing all notes associated with this object.
        """
        try:
            return self._notes
        except AttributeError:
            return Note([])  # No notes, so just return empty list.

    @notes.setter
    def notes(self, text_or_notes):
        """
        Set notes for this object.

        Args:
            text_or_notes: Text string or Note object to associate with this object.
        """
        if not text_or_notes:
            return
        self._notes = Note(text_or_notes)

    @notes.deleter
    def notes(self):
        """Remove all notes from this object."""
        try:
            del self._notes
        except AttributeError:
            pass

    @property
    def hiertuple(self):
        """Return a tuple containing the hierarchical path of this object."""
        try:
            return self.node.hiertuple
        except AttributeError:
            return tuple()

    @property
    def hierpath(self):
        """Return a string containing the hierarchical path of this object."""

        return HIER_SEP.join(self.hiertuple)

    @property
    def hiername(self):
        """
        Return the hierarchical name of the part.
        
        Returns:
            str: The hierarchical name including hierarchy prefix and tag.
        """

        return self.hierpath + HIER_SEP + (getattr(self, "tag", None) or getattr(self, "ref", self.name))

                
    def src_line(self, track_abs_path=False):
        """
        Return the file name and line number where the object was instantiated.

        Args:
            track_abs_path (bool): If True, use the absolute path of the file.
                                   If False, use the relative path from the script directory.
        
        Returns:
            str: File name and line number separated by colon.
        """
        try:
            file_path, file_line = self.skidl_trace[-1]
        except (AttributeError, IndexError):
            # If skidl_trace is not set or empty, return an empty string.
            return ""
        if not track_abs_path:
            file_path = os.path.relpath(file_path, self.circuit.script_dir)
        return file_path + ":" + file_line

