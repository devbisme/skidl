# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Base object for Circuit, Interface, Package, Part, Net, Bus, Pin objects.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import inspect
from builtins import object, range, str, super
from collections import namedtuple
from copy import deepcopy

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .alias import Alias
from .note import Note
from .utilities import export_to_all


__all__ = ["OK", "WARNING", "ERROR"]

OK, WARNING, ERROR = list(range(3))


@export_to_all
class SkidlBaseObject(object):

    # These are fallback lists so every object will have them to reference.
    erc_list = list()
    erc_assertion_list = list()

    def __init__(self):
        self.fields = {}

    def __getattr__(self, key):
        try:
            # Don't use super()!! It leads to long run times on Python 2.7.
            return self.__getattribute__("fields")[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        if key == "fields" or key not in self.fields:
            super().__setattr__(key, value)
        else:
            self.fields[key] = value

    def copy(self):
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
        """Run ERC on this object."""

        # Run ERC functions.
        self._exec_erc_functions(*args, **kwargs)

        # Run ERC assertions.
        self._eval_erc_assertions()

    def add_erc_function(self, func):
        """Add an ERC function to a class or class instance."""

        self.erc_list.append(func)

    def add_erc_assertion(self, assertion, fail_msg="FAILED", severity=ERROR):
        """Add an ERC assertion to a class or class instance."""

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
        Evaluate assertions for this object.
        """

        from .logger import active_logger

        def erc_report(evtpl):
            log_msg = "{evtpl.stmnt} {evtpl.fail_msg} in {evtpl.filename}:{evtpl.lineno}:{evtpl.function}.".format(
                evtpl=evtpl
            )
            if evtpl.severity == ERROR:
                active_logger.error(log_msg)
            elif evtpl.severity == WARNING:
                active_logger.warning(log_msg)

        for evtpl in self.erc_assertion_list:
            if eval(evtpl.stmnt, evtpl.globals, evtpl.locals) == False:
                erc_report(evtpl)

    def _exec_erc_functions(self, *args, **kwargs):
        """
        Execute ERC functions on a class instance.

        Args:
            args, kwargs: Arbitary argument lists to pass to the functions
                that are executed. (All functions get the same arguments.)
        """

        # Execute any instance functions for this particular instance.
        for f in self.erc_list:
            f(self, *args, **kwargs)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, nm):
        del self.name  # Remove any pre-existing name.
        self.aliases += nm
        self._name = nm

    @name.deleter
    def name(self):
        try:
            self.aliases.discard(self._name)
            self._name = None
        except AttributeError:
            pass

    @property
    def aliases(self):
        try:
            return self._aliases
        except AttributeError:
            return Alias([])  # No aliases, so just return an empty list.

    @aliases.setter
    def aliases(self, name_or_list):
        if not name_or_list:
            return
        self._aliases = Alias(name_or_list)

    @aliases.deleter
    def aliases(self):
        try:
            del self._aliases
        except AttributeError:
            pass

    @property
    def notes(self):
        try:
            return self._notes
        except AttributeError:
            return Note([])  # No notes, so just return empty list.

    @notes.setter
    def notes(self, text_or_notes):
        if not text_or_notes:
            return
        self._notes = Note(text_or_notes)

    @notes.deleter
    def notes(self):
        try:
            del self._notes
        except AttributeError:
            pass
