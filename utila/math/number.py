# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import typing

Number = typing.TypeVar('Number', int, float)  # pylint:disable=C0103
Numbers = typing.List[Number]  # pylint:disable=C0103

Floats = typing.List[float]
Ints = typing.List[int]


def numbers(items: typing.List) -> Numbers:
    """Convert iterable `items` to list of int's. Replace none
    convertable items to `None`.

    Args:
        items: iterable with items to convert
    Returns:
        List of int's or None's.

    >>> numbers(['1', '3', '5', 'wasd'])
    [1, 3, 5, None]
    """
    result = []
    for item in items:
        try:
            result.append(int(item))
        except ValueError:
            result.append(None)
    return result


def mins(*items: float) -> Number:
    """Determine minimum of passed `items`.

    >>> mins(1.0)
    1.0
    >>> mins([1,0,-5,3], 2, 3)
    -5
    """
    result = []
    for item in items:
        try:
            result.extend(item)
        except TypeError:
            result.append(item)
    value = min(result)
    return value


def maxs(*items: float) -> Number:
    """Determine maximum of passed `items`.

    >>> maxs(231.0)
    231.0
    >>> maxs([1,0,-5,3], 2, 3)
    3
    """
    result = []
    for item in items:
        try:
            result.extend(item)
        except TypeError:
            result.append(item)
    value = max(result)
    return value


def limit(*items: Numbers, maxvalue: Number) -> Number:
    """Limit collection by `maxvalue`.

    >>> limit(1, 2, 3, maxvalue=2.5)
    2.5
    >>> limit([1, 0, -5, 3], 2, maxvalue=3.5)
    3
    """
    return mins(maxs(*items), maxvalue)


def least(*items: Numbers, minvalue: Number) -> Number:
    """Define a least `minvalue` minimal value.

    >>> least([1, 0, -5, 3], 2, minvalue=3.5)
    3.5
    >>> least(10, 2, minvalue=3.5)
    10
    """
    return maxs(*items, minvalue)
