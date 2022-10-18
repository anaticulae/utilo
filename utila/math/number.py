# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math
import random
import typing

import utila

Number = typing.TypeVar('Number', int, float)  # pylint:disable=C0103
Numbers = list[Number]  # pylint:disable=C0103

Floats = list[float]
Ints = list[int]


def numbers(items: list) -> Numbers:
    """Convert iterable `items` to list of int's. Replace none
    convertible items to `None`.

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
    >>> mins([1, 0, -5, 3], 2, 3)
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
    >>> maxs([1, 0, -5, 3], 2, 3)
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


def threshold(item, diff: float, center: float = 0.0) -> float:
    """\
    >>> threshold(7.5, diff=3.0, center=5.0)
    5.0
    >>> threshold(2.0, diff=3.0, center=5.0)
    5.0
    >>> threshold(2.5, diff=5.0, center=0.0)
    0.0
    """
    if math.fabs(center - item) <= diff:
        return center
    return item


def between(border: list, func: callable = None):
    """\
    >>> between([10, 17, 23])
    (13.5, 20.0)
    """
    assert utila.isascending(border), str(border)
    if func is None:
        func = lambda first, second: (first + second) / 2  # pylint:disable=C3001
    result = [
        func(first, second) for first, second in zip(border[:-1], border[1:])
    ]
    result = tuple(result)
    result = utila.roundme(result, convert=False)
    return result


def numbers_random(  # pylint:disable=inconsistent-return-statements
    count: int = 1,
    mini: float = 0.0,
    maxi: float = 1.0,
    seed: float = None,
):
    """Generate random numbers.

    >>> list(numbers_random(count=2, mini=10, maxi=35, seed=1.0))
    [13.3591..., 31.185...]

    # >>> numbers_random(count=1, seed=1.0)
    # 0.134...
    """
    generator = random
    if seed is not None:
        generator: 'Random' = random.Random(seed)  # nosec
    if count == 1:
        return mini + (generator.random() * (maxi - mini))
    for _ in range(count):
        yield mini + generator.random() * (maxi - mini)


def iseven(number: int) -> bool:
    """\
    >>> iseven(3)
    False
    >>> iseven('10')
    True
    >>> iseven(0)
    True
    """
    # WHAT A BABY FUNCTION :|
    if isinstance(number, str):
        number = int(number)
    if not number % 2:
        return True
    return False


def isodd(number: int) -> bool:
    """\
    >>> isodd(5)
    True
    """
    return not iseven(number)
