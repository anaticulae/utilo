#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
import contextlib
import typing

from utila.logger import error
from utila.logger import log
from utila.logger import log_stacktrace
from utila.utils import FAILURE


@contextlib.contextmanager
def handle_error(*exceptions: typing.Tuple, code: int = FAILURE):
    """Catch given `exceptions` and print there message to `stderr`.
    Exit system with given `code`.

    Args:
        exceptions(iterable): of exception, which are handle by this context
        code(int): returned error-code
    Yields:
        NoReturn: run context which can raise Exception
    Raises:
        SystemExit: if given `exceptions` is raised while executing
        contextmanager.
    """
    try:
        yield
    except exceptions as msg:
        error(msg)
        exit(code)


CANCELLED_BY_USER = 130


def saveme(func=None, *, systemexit=True) -> callable:
    """Protect against KeyboardInterrupt and beautify Exceptions

    Args:
        func(callable): function which is invoked savely
        systemexit(bool): return exit value of quit with SystemExit
    Returns:
        decorated function
    """

    def decorating_function(user_function):

        def wrapper(*args, **kwds):
            ret = None
            try:
                ret = user_function(*args, **kwds)
            except KeyboardInterrupt:
                log('\nOperation cancelled by user')
                ret = CANCELLED_BY_USER
            except Exception as msg:  # pylint: disable=broad-except
                error(msg)
                log_stacktrace()
                ret = FAILURE
            if systemexit:
                exit(ret)
            return ret

        return wrapper

    # support @decorator() and @decorator
    if func is None:
        return decorating_function
    return decorating_function(func)
