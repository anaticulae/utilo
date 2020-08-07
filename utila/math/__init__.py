# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import enum
import math
import operator
import statistics
import typing

import utila.math.number

# default number of digits to round
NDIGITS = 2


def roundme(
        *items: float,
        digits: int = NDIGITS,
        convert: bool = True,
) -> float:
    """Round `items` to `NDIGITS.

    This method supports to round floats, tuple/list of floats. The
    passed datatype stays the same.

    >>> roundme(1.55, 2.50, 3.06, digits=1)
    [1.6, 2.5, 3.1]
    >>> roundme([1.5, 2.5, 3.2])
    [1.5, 2.5, 3.2]
    >>> roundme((1.53333, 2.5666, 3.21111), digits=3)
    (1.533, 2.567, 3.211)
    >>> roundme([10.5], digits=0, convert=False)
    [10.0]
    >>> roundme([10.5], digits=0)
    10.0

    Args:
        items: list of floats or a single float
        digits(int): amout of numbers after dot
        convert(bool): convert single iter item to float
    Raises:
        ValueError: if no float or list/tuple of numbers is passed
    Returns:
        List of round `items` or a single rounded item.
    """
    assert digits >= 0, f'negative digits {digits}'
    result = None
    try:
        result = [round(item, digits) for item in items]
    except TypeError as error:
        # support roundme([1,2,3]); roundme((1.5,2.33,3.2))
        if not isinstance(items[0], (list, tuple)):
            msg = f'require float, list or tuple, not: "{items}"'
            raise ValueError(msg) from error
        result = [roundme(item, digits=digits) for item in items[0]]
        if isinstance(items[0], tuple):
            # ensure that input which was a tuple stays a tuple
            result = tuple(result)
    if len(result) == 1 and convert:
        return result[0]
    return result


def isascending(
        items: 'utila.math.number.Numbers',
        strict: bool = True,
) -> bool:
    """Check that `items` are ascending numbers.

    >>> isascending([1, 2, 3, 4])
    True
    >>> isascending((5, 2.2, 5))
    False
    >>> isascending([1, 2, 2, 2, 3], strict=False)
    True
    """
    items = [int(item) for item in items]
    diff = [
        (after - current) for (current, after) in zip(items[:-1], items[1:])
    ]
    if strict:
        return all([item > 0 for item in diff])
    return all([item >= 0 for item in diff])


def modes(data: 'utila.math.number.Numbers') -> 'utila.math.number.Number':
    """Return the most common data point from discrete or nominal data.

    It is possible to have multiple common data points, there are sorted
    ascending.

    >>> modes((1,1,2,2))
    [1, 2]

    See: statistics.mode

    Args:
        data: list of numbers
    Raises:
        StatisticsError: if data is empty
    Returns:
        Most common number.
    """
    if not data:
        raise statistics.StatisticsError('no mode for empty data')
    table = statistics._counts(data)  # pylint:disable=W0212
    if len(table) == 1:
        return table[0][0]
    current = sorted([item[0] for item in table])
    return current


def mode(items, minimize: bool = False):
    """Determine single mode out of `items`.

    >>> mode((1,1,2,2))
    2
    >>> mode((1,1,2,2), minimize=True)
    1
    """
    result = modes(items)
    try:
        return result[0] if minimize else result[-1]
    except TypeError:
        return result


def diff_mode(
        items: 'utila.math.number.Numbers',
        max_diff: float = 2.0,
) -> 'utila.math.number.Numbers':
    """Compute mode of `item` and determine matched `items` which does
    not more differ than `max_diff` from mode.

    >>> diff_mode([1,1,3,5])
    [1, 1, 3]

    Args:
        items(Numbers): items to filter
        max_diff(float): max difference to mode which matches the classifier
    Returns:
        matched items
    """
    mode_ = mode(items)
    matched = [item for item in items if math.fabs(item - mode_) <= max_diff]
    return matched


class Strategy(enum.Enum):
    LOWER = enum.auto()
    UPPER = enum.auto()
    LINEARISE = enum.auto()


def lookup(
        value: 'utila.math.number.Number',
        table: typing.List,
        strategy: Strategy = None,
        right_outranges_none: bool = True,
        left_outranges_none: bool = True,
) -> 'utila.math.number.Number':
    """Use table lookup to determine holy value.

    Out of Bounds:
    >>> lookup(0, [(10,10), (20, 30), (30, 0.5)])
    >>> lookup(40, [(10,10), (20, 30), (30, 0.5)])

    Out of Bounds with backup:
    >>> lookup(40, [(10,10), (20, 30), (30, 0.5)], right_outranges_none=False)
    0.5
    >>> lookup(0, [(10,10), (20, 30), (30, 0.5)], left_outranges_none=False)
    10

    Different strategies:
    >>> lookup(30, [(10,10), (20, 30), (30, 0.5)], strategy = Strategy.UPPER)
    0.5
    >>> lookup(15, [(10,10), (20, 30), (30, 0.5)])
    10
    >>> lookup(15, [(10,10), (20, 30), (30, 0.5)], strategy = Strategy.LINEARISE)
    20.0

    Args:
        value: selector to determine holy value
        table: contains holy values to determine on given `value`.
        strategy: select left, right or linerise
        right_outranges_none: True: if lookup outranges return None
                              False: if lookup outrange use maxvalue
        left_outranges_none: True: if lookup outranges return None
                             False: if lookup outrange use minvalue
    Returns:
        determined value
    """
    # TODO: VERY SLOW
    assert len(table) >= 2, f'invalid data table: {table}'
    if strategy is None:
        strategy = Strategy.LOWER
    if value < table[0][0]:
        return None if left_outranges_none else table[0][1]
    if value > table[-1][0]:
        return None if right_outranges_none else table[-1][1]
    lower, result_lower = table[0]
    for upper, result_upper in table[1:]:
        if lower <= value <= upper:
            if strategy == Strategy.LINEARISE:
                diff = upper - lower
                mo = (result_upper - result_lower) / diff  # pylint:disable=C0103
                return result_lower + mo * (value - lower)
            if strategy == Strategy.LOWER:
                return result_lower
            return result_upper  # if strategy == Strategy.UPPER: always upper
        lower, result_lower = upper, result_upper
    return None


def diffs(items: 'utila.math.number.Numbers') -> 'utila.math.number.Numbers':
    """Difference between current and successor.

    >>> diffs([1, 5, 10, 5.5])
    [4.0, 5.0, 4.5]
    """
    assert len(items) >= 2, f'no enough items: {len(items)}'
    result = [
        math.fabs(first - second) for first, second in zip(
            items[1:],
            items[0:-1],
        )
    ]
    return result
