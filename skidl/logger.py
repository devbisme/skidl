# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) 2016-2021 Dave Vandenbout.

"""
Logging for generic messages and ERC.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import sys
from builtins import object, super

from future import standard_library

from .scriptinfo import get_script_name
from .skidlbaseobj import WARNING

standard_library.install_aliases()


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
            self.filename = None  # Prevents future error when removing non-existent log file.
            print(e)

    def remove_log_file(self):
        if self.filename:
            f_name = self.filename     # Close file handle before removing file.
            self.close()
            os.remove(f_name)
        self.filename = None


class SkidlLogger(logging.getLoggerClass()):
    """SKiDL logger that can stop output to log files and delete them."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_file_handlers = []

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
        # Stop file outputs for all log file handlers of this logger.
        for handler in self.log_file_handlers[:]:
            self.removeHandler(handler)


def _create_logger(title, log_msg_id="", log_file_suffix=".log"):
    """
    Create a logger, usually for run-time errors or ERC violations.
    """

    logging.setLoggerClass(SkidlLogger)
    logger = logging.getLogger(title)

    # Errors & warnings always appear on the terminal.
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter(log_msg_id + "%(levelname)s: %(message)s"))
    logger.addHandler(handler)

    # Errors and warnings are stored in a log file with the top-level script's name.
    handler = SkidlLogFileHandler(get_script_name() + log_file_suffix, mode="w")
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter(log_msg_id + "%(levelname)s: %(message)s"))
    logger.addHandler(handler)

    # Set logger to trigger on info, warning, and error messages.
    logger.setLevel(logging.INFO)

    # Augment the logger's functions to count the number of errors and warnings.
    logger.error = CountCalls(logger.error)
    logger.warning = CountCalls(logger.warning)

    return logger


###############################################################################
# Set up global loggers for runtime messages and ERC reports.

logger = _create_logger("skidl")
erc_logger = _create_logger("ERC_Logger", "ERC ", ".erc")

###############################################################################
