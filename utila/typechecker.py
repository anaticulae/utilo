# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
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


def asserts_types(items, types):
    """Ensure that `items` is a list and the types of the single `items`
    matches width `types`.

    >>> asserts_types([1, 3, 5, 10], int)

    >>> asserts_types([1, 'hello', 10], str)  #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AssertionError: [False, True, False]
    """
    assert isinstance(items, (list, tuple)), type(items)
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


def isint(item: str) -> bool:
    """Check if `item` is a int.

    >>> isint('ten')
    False
    >>> isint(10.5)
    False
    >>> isint('3')
    True
    >>> isint(0)
    True
    """
    with contextlib.suppress(ValueError):
        _ = int(str(item))
        return True
    return False


def equal_length(*items) -> bool:
    """\
    >>> equal_length([1, 2], (2,), [3, 3, 3])
    False
    >>> equal_length((1,), (2,))
    True
    >>> equal_length([3, 3, 3], [3, 3, 3])
    True
    """
    length = {len(item) for item in items}
    if len(length) > 1:
        return False
    return True


def isfloat(*floats) -> bool:
    """\
    >>> isfloat(1.0)
    True
    >>> isfloat(1)
    False
    >>> isfloat(1.5, 'test')
    False
    >>> isfloat(1.5, 3.0, -0.3)
    True
    """
    for item in floats:
        if not isinstance(item, float):
            return False
    return True


def asserts(item, typ):
    """\
    >>> asserts('hello', int)
    Traceback (most recent call last):
        ...
    AssertionError: require: <class 'int'>, got: <class 'str'>, raw:
    'hello'
    """
    if isinstance(item, typ):
        return
    msg = f'require: {typ}, got: {type(item)}, raw:\n{item!r}'
    raise AssertionError(msg)


def hasattribute(caller, attribute) -> bool:
    """\
    >>> hasattribute(hasattribute, 'caller')
    True
    >>> hasattribute(hasattribute, 'false')
    False
    """
    parameters = attributes(caller)
    if attribute in parameters:
        return True
    return False


def attributes(method: callable) -> tuple:
    """\
    >>> attributes(attributes)
    ('method',)
    """
    sig = inspect.signature(method)
    result = tuple(sig.parameters.keys())
    return result
