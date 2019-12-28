# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import functools
import inspect

from utila.logger import error


def checkdatatype(func) -> callable:
    """Decorator to ensure that passed data matches with defined datatype.

    Args:
        func(callable): function to ensure correct data input
    Returns:
        ensured callable
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        parameter = list(inspect.signature(func).parameters.items())
        parameter = [(name, item.annotation) for (name, item) in parameter]

        msg = 'parameter: %s, expected: %r, current %r:'
        errors = []
        for current, (name, expected) in zip(args, parameter):
            if isinstance(current, expected):
                continue
            if expected is inspect.Signature.empty:
                continue
            errors.append((msg % (name, expected, type(current))))
            errors.append(str(current))
        if errors:
            uf_name = func.__name__
            error('invalid function input `%s`' % uf_name)
            for item in errors:
                error(item)
            raise ValueError('invalid function input %s' % uf_name)
        return func(*args, **kwargs)

    return wrapper
