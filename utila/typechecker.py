# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from inspect import Signature
from inspect import signature

from utila.logging import logging_error

# TODO: USE functools.update_wrapper

def checkdatatype(func):
    """Check that passed arguments have the right datatype"""

    def decorating_function(user_function):

        def wrapper(*args, **kwds):
            uf_name = user_function.__name__
            parameter = list(signature(user_function).parameters.items())
            parameter = [(name, item.annotation) for (name, item) in parameter]

            msg = 'parameter: %s, expected: %r, current %r:'
            error = []
            for current, (name, expected) in zip(args, parameter):
                if isinstance(current, expected):
                    continue
                if expected is Signature.empty:
                    continue
                error.append((msg % (name, expected, type(current))))
                error.append(str(current))
            if error:
                logging_error('Invalid function input `%s`' % uf_name)
                for item in error:
                    logging_error(item)
                raise ValueError('Invalid function input %s' % uf_name)
            return user_function(*args, **kwds)

        wrapper.__userfunc__ = user_function
        return wrapper

    return decorating_function(func)
