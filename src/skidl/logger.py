# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Logging for generic messages and ERC.
"""

from __future__ import (  # isort:skip
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
import os
import queue
import sys
from builtins import object, super

try:
    from future import standard_library
    standard_library.install_aliases()
except ImportError:
    pass

from .scriptinfo import get_script_name, get_skidl_trace
from .skidlbaseobj import WARNING
from .utilities import export_to_all


__all__ = ["rt_logger", "erc_logger", "active_logger"]


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

    def reset(self):
        self.count = 0


class SkidlLogFileHandler(logging.FileHandler):
    """Logger that outputs messages to a file."""

    def __init__(self, *args, **kwargs):
        try:
            self.filename = kwargs["filename"]
        except KeyError:
            self.filename = args[0]
        try:
            super().__init__(*args, **kwargs)
        except PermissionError as e:
            # Prevents future error when removing non-existent log file.
            self.filename = None
            print(e)

    def remove_log_file(self):
        if self.filename:
            # Close file handle before removing file.
            f_name = self.filename
            self.close()
            os.remove(f_name)
        self.filename = None


class SkidlLogger(logging.getLoggerClass()):
    """SKiDL logger that can stop output to log files and delete them."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_file_handlers = []
        self.set_trace_depth(0)

    def addHandler(self, handler):
        if isinstance(handler, SkidlLogFileHandler):
            # Store handlers that output to files so they can be accessed later.
            self.log_file_handlers.append(handler)
        super().addHandler(handler)

    def removeHandler(self, handler):
        if handler in self.log_file_handlers:
            # Remove log files when a log file handler is removed.
            handler.remove_log_file()
            # Remove handler from list of log file handlers.
            self.log_file_handlers.remove(handler)
        super().removeHandler(handler)

    def stop_file_output(self):
        """Stop file outputs for all log handlers of this logger."""
        for handler in self.log_file_handlers[:]:
            self.removeHandler(handler)

    def set_trace_depth(self, depth):
        self.trace_depth = depth

    def get_trace(self):
        if self.trace_depth <= 0:
            return ""
        trace = get_skidl_trace()
        start = len(trace) - self.trace_depth
        return " @ [" + "=>".join(trace[start:]) + "]"

    def debug(self, msg, *args, **kwargs):
        super().debug(msg + self.get_trace(), *args, **kwargs)

    def summary(self, msg, *args, **kwargs):
        super().info(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        super().info(msg + self.get_trace(), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        super().warning(msg + self.get_trace(), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        super().error(msg + self.get_trace(), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        super().critical(msg + self.get_trace(), *args, **kwargs)

    def raise_(self, exc_class, msg):
        """Issue a logging message and then raise an exception.

        Args:
            exc_class (Exception class): Class of exception to raise.
            msg (string): Error message.

        Raises:
            exc_class: Exception class that is raised after error message is logged.
        """
        self.error(msg)
        raise exc_class(msg)

    def report_summary(self, phase_desc):
        """Report total of logged errors and warnings.

        Args:
            phase_desc (string): description of the phase of operations (e.g. "generating netlist").
        """
        if (self.error.count, self.warning.count) == (0, 0):
            self.summary("No errors or warnings found while {}.\n".format(phase_desc))
        else:
            self.summary(
                "{} warnings found while {}.".format(
                    active_logger.warning.count, phase_desc
                )
            )
            self.summary(
                "{} errors found while {}.\n".format(
                    active_logger.error.count, phase_desc
                )
            )


class ActiveLogger(SkidlLogger):
    """Currently-active logger for a given phase of operations."""

    def __init__(self, logger):
        """Create active logger.

        Args:
            logger (SkidlLogger): Logger that will be used for current phase of operations.
        """
        self.prev_loggers = queue.LifoQueue()
        self.set(logger)

    def set(self, logger):
        """Set the active logger.

        Args:
            logger (SkidlLogger): Logger that will be used for current phase of operations.
        """
        self.current_logger = logger
        self.__dict__.update(self.current_logger.__dict__)

    def push(self, logger):
        """Save the currently active logger and activate the given logger.

        Args:
            logger (SkidlLogger): Logger to be activated.
        """
        self.prev_loggers.put(self.current_logger)
        self.set(logger)

    def pop(self):
        """Re-activate the previously active logger."""
        self.set(self.prev_loggers.get())


def _create_logger(title, log_msg_id="", log_file_suffix=".log"):
    """
    Create a logger, usually for run-time errors or ERC violations.
    """

    logging.setLoggerClass(SkidlLogger)
    logger = logging.getLogger(title)

    # Errors & warnings always appear on the terminal.
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(log_msg_id + "%(levelname)s: %(message)s"))
    logger.addHandler(handler)

    # Errors and warnings are stored in a log file with the top-level script's name.
    handler = SkidlLogFileHandler(get_script_name() + log_file_suffix, mode="w")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(log_msg_id + "%(levelname)s: %(message)s"))
    logger.addHandler(handler)

    # Set logger to trigger on info, warning, and error messages.
    logger.setLevel(logging.INFO)

    # Augment the logger's functions to count the number of errors and warnings.
    logger.error = CountCalls(logger.error)
    logger.warning = CountCalls(logger.warning)

    return logger


@export_to_all
def stop_log_file_output(stop=True):
    """Permanently stop loggers from creating files containing log messages."""
    if stop:
        rt_logger.stop_file_output()
        erc_logger.stop_file_output()


###############################################################################

# Create loggers for runtime messages and ERC reports.
rt_logger = _create_logger("skidl")
rt_logger.set_trace_depth(2)
erc_logger = _create_logger("ERC_Logger", "ERC ", ".erc")
erc_logger.set_trace_depth(0)

# Create active logger that starts off as the runtime logger.
active_logger = ActiveLogger(rt_logger)

###############################################################################
