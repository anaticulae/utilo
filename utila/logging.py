#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import sys
from contextlib import contextmanager
from time import time
from traceback import format_exc

from utila.utils import NEWLINE
from utila.utils import forward_slash


def logging(msg: str = '', end: str = NEWLINE):
    """Write message to logger

    Args:
        msg(str): message to log
        end(str): lineending
    Hint:
        Logging with default arguments will log a newline
    """
    # TODO: msg = NEWLINE.join(wrap(msg, 120))
    msg = forward_slash(msg)
    print(msg, end=end, file=sys.stdout, flush=True)


def logging_error(msg: str):
    """Print error-message to stderr and add [ERROR]-tag"""
    # use forward slashs
    msg = forward_slash(msg)
    print('[ERROR] %s' % msg, file=sys.stderr)


def logging_stacktrace():
    stack_trace = format_exc()
    logging_error(forward_slash(stack_trace))


def flush():
    """Flush stdout"""
    print('', end='', file=sys.stdout, flush=True)


def print_runtime(before: int):
    """Determine runtime due the diff of current time and provided time
    `before`. Log this timediff.

    Args:
        before(int): time recorded some time before - use time.time()
    """
    time_diff = time() - before
    logging('Runtime: %.2f secs' % time_diff)


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
