# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Logging system for SKiDL.

This module provides logging functionality for runtime messages and electrical rule checking.
It includes specialized loggers that can output to both the console and log files,
with support for counting errors and warnings, and managing log file creation and deletion.
The module also provides context management for temporarily changing the active logger.
"""

import logging
import os
import queue
import sys

from .scriptinfo import get_script_name, get_skidl_trace
from .skidlbaseobj import WARNING
from .utilities import export_to_all


__all__ = ["rt_logger", "erc_logger", "active_logger"]


class CountCalls(object):
    """
    Decorator for counting the number of times a function is called.
    
    This decorator tracks calls to logging functions, making it easy
    to determine if and how many errors/warnings were issued during
    circuit processing or ERC.
    
    Args:
        func (function): The function to be wrapped and counted.
    """

    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        """
        Call the wrapped function and increment the call counter.
        
        Args:
            *args: Arguments to pass to the wrapped function.
            **kwargs: Keyword arguments to pass to the wrapped function.
            
        Returns:
            The return value from the wrapped function.
        """
        self.count += 1
        return self.func(*args, **kwargs)

    def reset(self):
        """Reset the call counter to zero."""
        self.count = 0


class SkidlLogFileHandler(logging.FileHandler):
    """
    Logger handler that outputs messages to a file with enhanced file handling.
    
    This extends the standard FileHandler with functionality to track
    filenames and remove log files when the handler is closed or removed.
    
    Args:
        *args: Arguments to pass to FileHandler.
        **kwargs: Keyword arguments to pass to FileHandler.
    """

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
        """
        Close and remove the log file associated with this handler.
        
        If the file doesn't exist or can't be removed, the filename is set to None.
        """
        if self.filename:
            # Close file handle before removing file.
            f_name = self.filename
            self.close()
            os.remove(f_name)
        self.filename = None


class SkidlLogger(logging.getLoggerClass()):
    """
    SKiDL logger with enhanced functionality for managing file output and context.
    
    This extends the standard Logger class with methods to manage file output handlers,
    control stack trace depth in messages, and provide better formatted error/warning messages.
    
    Args:
        *args: Arguments to pass to Logger.
        **kwargs: Keyword arguments to pass to Logger.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_file_handlers = []
        self.set_trace_depth(0)

    def addHandler(self, handler):
        """
        Add a handler to the logger and track file handlers separately.
        
        Args:
            handler (logging.Handler): The handler to add.
        """
        if isinstance(handler, SkidlLogFileHandler):
            # Store handlers that output to files so they can be accessed later.
            self.log_file_handlers.append(handler)
        super().addHandler(handler)

    def removeHandler(self, handler):
        """
        Remove a handler from the logger and clean up any associated log file.
        
        Args:
            handler (logging.Handler): The handler to remove.
        """
        if handler in self.log_file_handlers:
            # Remove log files when a log file handler is removed.
            handler.remove_log_file()
            # Remove handler from list of log file handlers.
            self.log_file_handlers.remove(handler)
        super().removeHandler(handler)

    def stop_file_output(self):
        """
        Stop file output for all log handlers of this logger.
        
        This removes all file handlers, which in turn removes their log files.
        """
        for handler in self.log_file_handlers[:]:
            self.removeHandler(handler)

    def set_trace_depth(self, depth):
        """
        Set the depth of stack trace to include in log messages.
        
        Args:
            depth (int): Number of stack frames to include in the trace.
                         0 means no trace information will be included.
        """
        self.trace_depth = depth

    def get_trace(self):
        """
        Get a string containing the current trace information.
        
        Returns:
            str: A string with the call stack trace or empty string if trace_depth <= 0.
        """
        if self.trace_depth <= 0:
            return ""
        trace = [file + ":" + line for file, line in get_skidl_trace()]
        start = len(trace) - self.trace_depth
        return " @ [" + "=>".join(trace[start:]) + "]"

    def debug(self, msg, *args, **kwargs):
        """
        Log a debug message with trace information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().debug(msg + self.get_trace(), *args, **kwargs)

    def summary(self, msg, *args, **kwargs):
        """
        Log a summary message without location information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().info(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log an info message with trace information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().info(msg + self.get_trace(), *args, **kwargs)

    def bare_info(self, msg, *args, **kwargs):
        """
        Log an info message without trace information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log a warning message with trace information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().warning(msg + self.get_trace(), *args, **kwargs)

    def bare_warning(self, msg, *args, **kwargs):
        """
        Log a warning message without trace information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log an error message with trace information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().error(msg + self.get_trace(), *args, **kwargs)

    def bare_error(self, msg, *args, **kwargs):
        """
        Log an error message without trace information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log a critical message with trace information.
        
        Args:
            msg (str): The message to log.
            *args: Arguments to pass to the logger.
            **kwargs: Keyword arguments to pass to the logger.
        """
        super().critical(msg + self.get_trace(), *args, **kwargs)

    def raise_(self, exc_class, msg):
        """
        Log an error message and then raise an exception.
        
        This method combines logging an error and raising an exception
        to simplify error handling code.
        
        Args:
            exc_class (Exception): The exception class to raise.
            msg (str): The error message to log and include in the exception.
            
        Raises:
            exc_class: The specified exception with the given message.
        """
        self.error(msg)
        raise exc_class(msg)

    def report_summary(self, phase_desc):
        """
        Report a summary of logged errors and warnings.
        
        Args:
            phase_desc (str): Description of the phase being summarized (e.g., "generating netlist").
        """
        if (self.error.count, self.warning.count, self.bare_error.count, self.bare_warning.count) == (0, 0, 0, 0):
            self.summary(f"No errors or warnings found while {phase_desc}.\n")
        else:
            self.summary(
                f"{active_logger.warning.count + active_logger.bare_warning.count} warnings found while {phase_desc}."
            )
            self.summary(
                f"{active_logger.error.count + active_logger.bare_error.count} errors found while {phase_desc}.\n"
            )


class ActiveLogger(SkidlLogger):
    """
    Logger that manages the currently active logging context.
    
    This class encapsulates a stack of loggers and enables temporary
    switching between different logging contexts, with clean restoration
    of the previous context when done.
    
    Args:
        logger (SkidlLogger): The initial logger to activate.
    """

    def __init__(self, logger):
        """
        Initialize the active logger with an initial logger.
        
        Args:
            logger (SkidlLogger): The logger that will be active initially.
        """
        self.prev_loggers = queue.LifoQueue()
        self.set(logger)

    def set(self, logger):
        """
        Set the active logger.
        
        Args:
            logger (SkidlLogger): Logger to make active.
        """
        self.current_logger = logger
        self.__dict__.update(self.current_logger.__dict__)

    def push(self, logger):
        """
        Save the currently active logger and activate a new one.
        
        This method puts the current logger on a stack and activates
        the provided logger in its place.
        
        Args:
            logger (SkidlLogger): New logger to activate.
        """
        self.prev_loggers.put(self.current_logger)
        self.set(logger)

    def pop(self):
        """
        Restore the previously active logger.
        
        This method deactivates the current logger and restores
        the logger that was active before the most recent push().
        """
        self.set(self.prev_loggers.get())


def _create_logger(title, log_msg_id="", log_file_suffix=".log"):
    """
    Create a customized logger for SKiDL.
    
    This function creates a logger with handlers for outputting to both
    the console and a log file, with proper formatting for SKiDL messages.
    
    Args:
        title (str): Name/title for the logger.
        log_msg_id (str, optional): Prefix for log messages.
        log_file_suffix (str, optional): Suffix for the log filename.
        
    Returns:
        SkidlLogger: Configured logger instance.
    """

    logging.setLoggerClass(SkidlLogger)
    logger = logging.getLogger(title)

    # Prevent the logger from propagating messages up to the root logger
    # so that messages are only sent to the handlers attached to this logger.
    logger.propagate = False

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
    logger.bare_error = CountCalls(logger.bare_error)
    logger.bare_warning = CountCalls(logger.bare_warning)

    return logger


@export_to_all
def stop_log_file_output(stop=True):
    """
    Stop or restart log file output for all loggers.
    
    Args:
        stop (bool, optional): True to stop file output, False to allow it.
            Defaults to True.
    """
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
