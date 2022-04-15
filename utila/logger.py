#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import enum
import functools
import inspect
import os
import subprocess  # nosec
import sys
import threading
import time
import traceback

import utila
# do not change import cause: if utilasafe is not installed, utila is not
# fully imported when utilasafe raises an error, therefore importing
# fix_encoding and forward_slash is important
from utila.string import fix_encoding
from utila.string import forward_slash
from utila.utils import NEWLINE


class Level(enum.IntEnum):
    LOGGING = 0
    CALLS = 1
    INFO = 2
    DEBUG = 3
    VERBOSE = 4
    ERROR = -1
    INFORMATION = 2  # TODO: REMOVE LATER


LEVEL_DEFAULT = Level.LOGGING
LEVEL = LEVEL_DEFAULT

# define output file where logs written to. If None, do nothing.
OUTFILE = None


def level_setup(level: Level):
    """\
    Use ints to choose logging level:
    >>> level_setup(2)
    >>> assert utila.level_current() == Level.INFO
    >>> level_setup(LEVEL_DEFAULT)
    """
    if isinstance(level, int):
        level = Level(level)
    global LEVEL  # pylint:disable=global-statement
    LEVEL = level


def outfile(path):
    global OUTFILE  # pylint:disable=global-statement
    OUTFILE = path


@contextlib.contextmanager
def level_tmp(level: Level):
    """Set logging level, yield context and reset to previous logging level."""
    before = level_current()
    level_setup(level)
    yield
    level_setup(before)


def level_current() -> Level:
    return LEVEL


def log(
    *msg: str,
    level: Level = Level.LOGGING,
    preserve_newlines: bool = True,
    end: str = NEWLINE,
):
    r"""Write message to logger.

    Args:
        msg(str): message to log
        level(Level): define logging level which is required to print on
                      console
        preserve_newlines(bool): if True, do not convert \n to /n
        end(str): line ending
    Hint:
        Logging with default arguments will log a newline
    """
    msg = utila.from_tuple(msg) if isinstance(msg, tuple) else msg
    if level == Level.ERROR:
        error(msg)
        return
    if level > LEVEL:
        return
    # avoid problems when using with windows console(cp1252)
    msg = fix_encoding(msg)
    # TODO: msg = NEWLINE.join(wrap(msg, 120))
    msg = forward_slash(msg, keep_newline=preserve_newlines)
    write_log(msg, end=end)
    print(msg, file=sys.stdout, end=end, flush=True)


@functools.lru_cache(maxsize=1024)
def warning(*msg: str, end: str = NEWLINE):
    """Log warning, mainly used for implementation problems.

    Cache warnings to log warning only once.
    """
    msg = utila.from_tuple(msg) if isinstance(msg, tuple) else msg
    log(f'    {msg}', level=Level.LOGGING, end=end)


def call(*msg: str, end: str = NEWLINE):
    msg = utila.from_tuple(msg) if isinstance(msg, tuple) else msg
    log(f'  {msg}', level=Level.CALLS, end=end)


def info(*msg: str, end: str = NEWLINE):
    msg = utila.from_tuple(msg) if isinstance(msg, tuple) else msg
    log(f'    {msg}', level=Level.INFO, end=end)


def debug(*msg: str, end: str = NEWLINE):
    msg = utila.from_tuple(msg) if isinstance(msg, tuple) else msg
    log(f'      {msg}', level=Level.DEBUG, end=end)


def verbose(*msg: str, end: str = NEWLINE):
    msg = utila.from_tuple(msg) if isinstance(msg, tuple) else msg
    log(f'        {msg}', level=Level.VERBOSE, end=end)


def error(msg: str, *, end: str = NEWLINE):
    """Print error-message to stderr and add [ERROR]-tag"""
    # avoid problems when using with windows console(cp1252)
    msg = fix_encoding(msg)
    # use forward slash's
    msg = forward_slash(msg, keep_newline=True)
    msg = f'[ERROR] {msg}'
    write_log(msg, end=end)
    print(msg, file=sys.stderr, end=end, flush=True)


SINGLE_LOGGING = threading.Semaphore()


def write_log(msg: str, end: str):
    if OUTFILE is None:
        return
    with SINGLE_LOGGING:
        # ensure that only one thread writes to file
        utila.file_append(OUTFILE, msg + end, create=True)


def print_stacktrace():
    stack_trace = traceback.format_exc()
    error(forward_slash(stack_trace, keep_newline=True))


def log_args(func) -> callable:
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
            log(f'call({func.__qualname__}) with:', level=MIN_LEVEL)
            for para, content in zip(parameter, args):
                content = str(content)[0:150]
                log(f'  {para[0]}: {content}', level=MIN_LEVEL)
            log('', level=MIN_LEVEL)
        return func(*args, **kwargs)

    return wrapper


def print_runtime(before: int, msg: str = '') -> float:
    """Determine runtime due the diff of current time and provided time
    `before`. Log this time diff.

    Args:
        before(int): time recorded some time before - use time.time()
        msg(str): extend runtime message to differentiate multiple invocations
    Returns:
        Runtime diff
    """
    time_diff = time.time() - before
    if msg:
        log('runtime(%s): %.2f secs' % (msg, time_diff))
    else:
        log('runtime: %.2f secs' % time_diff)
    return time_diff


def print_env():
    """Log environment variables as a table.

    Hint:
        Log level higher equal than `INFO` is required
    """
    for key, value in os.environ.items():
        info('{:<40}{}'.format(key, value))


def format_completed(completed: subprocess.CompletedProcess) -> str:
    """Format stdout, stderr and returncode of completed process as
    process overview

    Args:
        completed(subprocess.Completed): completed process
    Returns:
        formatted process
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


class profile(contextlib.ContextDecorator):  # pylint:disable=C0103
    """ContextManager and Decorator to profile method performance."""

    def __init__(self, msg: str = '', always: bool = False):
        """Print runtime to logger to monitor performance.

        Current log level must be higher than Level.LOGGING. Use -V to
        increase logging level.

        Args:
            msg(str): extend runtime message to differentiate multiple runtime
            always(bool): profile log level independent
        """
        self.msg = msg
        self.start = None
        self.diff = None
        self.always = always

    def __enter__(self):
        """Start profiler."""
        self.start = time.time()

    def __exit__(self, *exc_info):
        """Finish profiling."""
        if utila.level_current() == Level.LOGGING and not self.always:
            return
        self.diff = print_runtime(self.start, msg=self.msg)


class SkipCollector:
    """Context manager to handle selective pages."""

    def __init__(self, pages=None):
        """Initialize SkipCollector with `pages` which should not be skipped.

        Args:
            pages(list): list with pages which `skip(page)` return False
        """
        if isinstance(pages, int):  # convert single page set
            pages = [pages]
        self.pages = set(pages) if pages is not None else None
        self.data = []

    def skip(self, page: int) -> bool:
        if self.pages is not None and page not in self.pages:
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


def log_raw(content: str):
    """Print `content` which raises an AssertError.

    Fix encoding if non-utf8 character are printed.

    Hint: Avoid using print() to reduce finding 'print' when searching
    in code base.

    >>> log_raw('Hier Spricht Python')
    Hier Spricht Python

    Example:
        assert len(abc) > 100, utila.log_raw(abc)
    """
    content = fix_encoding(content)
    print(content, flush=True)


def print_banner(text, symbol='*', width=80, newlines: bool = True):
    """\
    >>> print_banner('hello', width=30)
    <BLANKLINE>
    ******************************
    **          hello           **
    ******************************
    <BLANKLINE>
    """
    newlines = '\n' if newlines else ''
    text = f'{text}'.center(width - 4)
    utila.log(newlines + symbol * width)
    utila.log(f'{symbol}{symbol}{text}{symbol}{symbol}')
    utila.log(symbol * width + newlines)


def log_return(func):
    """\
    >>> @log_return
    ... def func(items):
    ...     return 4
    >>> func((1,5,6,7,4,9))
    4
    """

    def logger(results):
        before = results
        selected = func(results)
        try:
            index = before.index(selected)
            utila.debug(f'{func.__name__} selected index: {index}')
        except ValueError:
            utila.error(f'{func.__name__} select {selected} is not possible')
        return selected

    return logger
