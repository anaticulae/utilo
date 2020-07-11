# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import functools
import inspect
import typing

import utila


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
            utila.error('invalid function input `%s`' % uf_name)
            for item in errors:
                utila.error(item)
            raise ValueError('invalid function input %s' % uf_name)
        return func(*args, **kwargs)

    return wrapper


Strings = typing.List[str]


def isstrings(items) -> bool:
    """Ensure to have list of str.

    >>> isstrings(['hello', 'my', 'man'])
    True
    >>> isstrings('test')
    False
    >>> isstrings(10)
    False
    >>> isstrings({'hi': 'me'})
    False
    """
    if not isinstance(items, list):
        return False
    try:
        return all((isinstance(item, str) for item in items))
    except TypeError:
        return False


def assert_type_list(items, types):
    """Ensure that `items` is a list and the types of the single `items`
    matches width `types`.

    >>> assert_type_list([1, 3, 5, 10], int)
    >>> assert_type_list([1, 'hello', 10], str)
    Traceback (most recent call last):
        ...
    AssertionError: [False, True, False]
    """
    assert isinstance(items, list), type(items)
    verified = [isinstance(item, types) for item in items]
    assert all(verified), str(verified)


def isnumber(item: str) -> bool:
    """Check if `item` is a number.

    >>> isnumber('ten')
    False
    >>> isnumber(10.5)
    True
    >>> isnumber('3.5')
    True
    >>> isnumber(None)
    False
    """
    with contextlib.suppress(ValueError):
        _ = float(str(item))
        return True
    return False
