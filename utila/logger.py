#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import sys
from contextlib import contextmanager
from enum import IntEnum
from time import time
from traceback import format_exc

from utila.utils import NEWLINE
from utila.utils import fix_encoding
from utila.utils import forward_slash


class Level(IntEnum):
    LOGGING = 0
    CALLS = 1
    INFORMATION = 2
    DEBUG = 3
    ERROR = -1


LEVEL = Level.LOGGING


def level_setup(level: Level):
    global LEVEL
    LEVEL = level


def log(msg: str = '', level: Level = Level.LOGGING, end: str = NEWLINE):
    """Write message to logger

    Args:
        msg(str): message to log
        level(Level): define logging level which is required to print on
                      console
        end(str): lineending
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


def call(msg: str):
    log('  %s' % msg, Level.CALLS)


def info(msg: str):
    log('    %s' % msg, Level.INFORMATION)


def debug(msg: str):
    log('      %s' % msg, Level.DEBUG)


def error(msg: str):
    """Print error-message to stderr and add [ERROR]-tag"""
    # avoid problems when using with windows console(cp1252)
    msg = fix_encoding(msg)
    # use forward slashs
    msg = forward_slash(msg)
    print('[ERROR] %s' % msg, file=sys.stderr, flush=True)


def log_stacktrace():
    stack_trace = format_exc()
    error(forward_slash(stack_trace))


def print_runtime(before: int):
    """Determine runtime due the diff of current time and provided time
    `before`. Log this timediff.

    Args:
        before(int): time recorded some time before - use time.time()
    """
    time_diff = time() - before
    log('Runtime: %.2f secs' % time_diff)


@contextmanager
def profile():
    """Print runtime to logger to monitore performance"""
    start = time()
    try:
        yield
    except Exception:
        print_runtime(start)
        raise
    else:
        print_runtime(start)
