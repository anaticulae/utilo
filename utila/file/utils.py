# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import inspect
import os

import utila

PATH_MAX_LENGTH = 512


def exists(path: str) -> bool:
    """Wrapper for os.path.exists with checking None and convert path to
    str if required.

    >>> exists(__file__)
    True
    >>> exists(None)
    False
    >>> exists(1234)
    False
    """
    if path is None:
        return False
    path = str(path)[0:PATH_MAX_LENGTH]
    return os.path.exists(path)


def exists_assert(path: str):
    assert os.path.exists(path), utila.shrink(str(path), maxlength=100)


def pathexists(func=None) -> callable:

    def decorating_function(user_function):

        def wrapper(*args, **kwds):
            sig = inspect.signature(user_function)
            try:
                path = kwds['path']
            except KeyError:
                parameter = list(item for item in sig.parameters)
                try:
                    pos = list(item for item in parameter).index('path')
                except ValueError:
                    raise TypeError(f'no `path` in {parameter}') from None
                path = args[pos]
            utila.exists_assert(path)
            ret = user_function(*args, **kwds)
            return ret

        return wrapper

    return decorating_function(func)
