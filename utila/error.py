#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import contextlib
import sys
import typing

import utila


@contextlib.contextmanager
def handle_error(*exceptions: typing.Tuple, code: int = None):
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
        utila.error(msg)
        code = code if code is not None else utila.FAILURE
        sys.exit(code)


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
                utila.log('\nOperation cancelled by user')
                ret = CANCELLED_BY_USER
            except Exception as msg:  # pylint: disable=broad-except
                utila.error(msg)
                utila.print_stacktrace()
                ret = utila.FAILURE
            if systemexit:
                sys.exit(ret)
            return ret

        return wrapper

    # support @decorator() and @decorator
    if func is None:
        return decorating_function
    return decorating_function(func)
