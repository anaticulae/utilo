#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import enum
import functools
import inspect
import os
import subprocess
import sys
import time
import traceback

from utila.string import fix_encoding
from utila.string import forward_slash
from utila.utils import NEWLINE


class Level(enum.IntEnum):
    LOGGING = 0
    CALLS = 1
    INFORMATION = 2
    DEBUG = 3
    ERROR = -1


LEVEL = Level.LOGGING


def level_setup(level: Level):
    global LEVEL  # pylint:disable=global-statement
    LEVEL = level


def log(msg: str = '', level: Level = Level.LOGGING, end: str = NEWLINE):
    """Write message to logger

    Args:
        msg(str): message to log
        level(Level): define logging level which is required to print on
                      console
        end(str): line ending
    Hint:
        Logging with default arguments will log a newline
    """
    if level == Level.ERROR:
        error(msg)
        return
    if level > LEVEL:
        return
    # avoid problems when using with windows console(cp1252)
    msg = fix_encoding(msg)
    # TODO: msg = NEWLINE.join(wrap(msg, 120))
    msg = forward_slash(msg)
    print(msg, end=end, file=sys.stdout, flush=True)


def call(msg: str, end: str = NEWLINE):
    log('  %s' % msg, Level.CALLS, end=end)


def info(msg: str, end: str = NEWLINE):
    log('    %s' % msg, Level.INFORMATION, end=end)


def debug(msg: str, end: str = NEWLINE):
    log('      %s' % msg, Level.DEBUG, end=end)


def error(msg: str, end: str = NEWLINE):
    """Print error-message to stderr and add [ERROR]-tag"""
    # avoid problems when using with windows console(cp1252)
    msg = fix_encoding(msg)
    # use forward slash's
    msg = forward_slash(msg)
    print('[ERROR] %s' % msg, file=sys.stderr, flush=True, end=end)


def log_stacktrace():
    stack_trace = traceback.format_exc()
    error(forward_slash(stack_trace))


def log_args(func):
    """Decorator to write passed arguments to function call. Log if
    logging `LEVEL` is higher equal than Level.CALLS.

    Args:
        func(callable): function to log name and input args
    Returns:
        wrapped function
    """
    MIN_LEVEL = Level.CALLS  # pylint:disable=C0103

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if LEVEL >= MIN_LEVEL:
            signature = inspect.signature(func)
            parameter = list(signature.parameters.items())
            log(msg=f'call({func.__qualname__}) with:', level=MIN_LEVEL)
            for para, content in zip(parameter, args):
                content = str(content)[0:150]
                log(msg=f'  {para[0]}: {content}', level=MIN_LEVEL)
            log('', level=MIN_LEVEL)
        return func(*args, **kwargs)

    return wrapper


def print_runtime(before: int, msg: str = ''):
    """Determine runtime due the diff of current time and provided time
    `before`. Log this time diff.

    Args:
        before(int): time recorded some time before - use time.time()
        msg(str): extend runtime message to differentiate multiple invocations
    """
    time_diff = time.time() - before
    if msg:
        log('Runtime(%s): %.2f secs' % (msg, time_diff))
    else:
        log('Runtime: %.2f secs' % time_diff)


def print_env():
    """Log environment variables as a table.

    Hint:
        Log level higher equal than `INFORMATION` is required
    """
    for key, value in os.environ.items():
        info('{:<40}{}'.format(key, value))


def format_completed(completed: subprocess.CompletedProcess) -> str:
    """Format stdout, stderr and returncode of completed process as
    process overview

    Args:
        completed(subprocess.Completed): completed process
    Returns:
        formated process
    Format:
        args: ...
        stdout: ...
        stderr: ...
        returncode: ...
    """
    stderr = completed.stderr if completed.stderr else 'stderr: empty!'
    stdout = completed.stdout if completed.stdout else 'stdout: empty!'
    msg = ('[process completed: start]\n'
           f'args: "{completed.args}"\n'
           f'stdout:\n{stdout}\n'
           f'stderr:\n{stderr}\n'
           f'returncode: {completed.returncode}\n'
           '[process completed: end]')
    return msg


@contextlib.contextmanager
def profile(msg: str = ''):
    """Print runtime to logger to monitor performance

    Args:
        msg(str): extend runtime message to differentiate multiple runtime
    """
    start = time.time()
    try:
        yield
    except Exception:
        print_runtime(start, msg=msg)
        raise
    else:
        print_runtime(start, msg=msg)


class SkipCollector:
    """Context manager to handle selective pages."""

    def __init__(self, pages):
        """Initialize SkipCollector with pages which should not be skipped

        Args:
            pages(list): list with pages which `skip(page)` return False
        """
        self.pages = pages
        self.data = []

    def skip(self, page):
        if self.pages and page not in self.pages:
            self.data.append(page)
            return True
        self.log()
        return False

    def log(self):
        """Print current state of skipped items and reset this state"""
        if self.data:
            msg = ', '.join([str(item) for item in self.data])
            debug(f'skip: {msg}')
        self.data = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # pylint:disable=W0621
        self.log()
