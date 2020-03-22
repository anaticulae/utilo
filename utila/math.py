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

# default number of digits to round
NDIGITS = 2

Number = typing.TypeVar('Number', int, float)  # pylint:disable=C0103
Numbers = typing.List[Number]  # pylint:disable=C0103

# x0, y0, x1, y1
Rectangle = typing.Tuple[float, float, float, float]
Rectangles = typing.List[Rectangle]


def roundme(*items: float, digits: int = NDIGITS) -> float:
    """Round `items` to `NDIGITS.

    This method supports to round floats, tuple/list of floats. The
    passed datatype stays the same.

    >>> roundme(1.55, 2.50, 3.06, digits=1)
    [1.6, 2.5, 3.1]
    >>> roundme([1.5, 2.5, 3.2])
    [1.5, 2.5, 3.2]
    >>> roundme((1.53333, 2.5666, 3.21111), digits=3)
    (1.533, 2.567, 3.211)

    Args:
        items: list of floats or a single float
        digits(int): amout of numbers after dot
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
    if len(result) == 1:
        return result[0]
    return result


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


def isascending(items: Numbers) -> bool:
    """Check that `items` are ascending numbers.

    >>> isascending([1, 2, 3, 4])
    True
    >>> isascending((5, 2.2, 5))
    False
    """
    items = [int(item) for item in items]
    diff = [
        (after - current) for (current, after) in zip(items[:-1], items[1:])
    ]
    return all([item >= 0 for item in diff])


def modes(data: Numbers, minimize: bool = True) -> Number:
    """Return the most common data point from discrete or nominal data.

    It is possible to have multiple common data points. To extract a
    unique point `minimize` enables to decide which number is used.

    See: statistics.mode

    Args:
        data: list of numbers
        minimize(bool): if True the biggest common number is used, if
                        not the smallest is used.
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
    if minimize:
        return current[0]
    return current[-1]


def near(first, second, diff: float = 2.0) -> bool:
    """Test that two items are close together.

    >>> near(2.1,-0.9, diff=3.0)
    True
    >>> near(1.0, 10, diff=1.0)
    False
    """
    return math.fabs(first - second) <= diff


def rectangle_merge(rectangles):
    """Reduce list of rectangles to the minimal list to describe the
    covered area. Remove rectangle when there have a parent rectangle
    which covers them.

    Note: This algoritm does not determine the optimal count of
    rectangles, if two rectangle cover the area of a third one, all
    three rectangle will be saved.

    >>> rectangle_merge([(50, 50, 100, 100), (20, 20, 100, 100)])
    [(20, 20, 100, 100)]
    >>> rectangle_merge([(50, 50, 100, 100), (100, 100, 150, 150)])
    [(50, 50, 100, 100), (100, 100, 150, 150)]
    >>> assert rectangle_merge([]) is None
    """
    if not rectangles:
        return None

    def merge(items):
        # sort top down, left right
        items = sorted(items, key=operator.itemgetter(1, 0))
        result = []
        while len(items) >= 2:
            item = items.pop()
            if any((rectangle_inside(check, item) for check in items)):
                continue
            else:
                result.insert(0, item)
        result.insert(0, items.pop())
        return result

    current = rectangles[:]
    merged = merge(current)
    while merged != current:
        # repeat till algorithm does not change the list
        current = merged
        merged = merge(current)
    return current


def rectangle_size(rectangle):
    """Determine area size of rectangle.

    >>> rectangle_size((50, 50, 100, 100))
    2500.0
    """
    width = rectangle[2] - rectangle[0]
    height = rectangle[3] - rectangle[1]
    area = math.fabs(width * height)
    area = roundme(area)
    return area


def rectangle_inside(first, second, diff: float = 0):
    """Is `second` rectangle in `first`.

    >>> rectangle_inside((0, 0, 100, 100), (50, 50, 100, 100))
    True
    >>> rectangle_inside((0, 0, 100, 100), (75, 75, 125, 125))
    False
    """
    diff = diff / 2
    x0, y0, x1, y1 = first
    x00, y00, x11, y11 = second
    return all((
        ((x0 - diff) <= x00 <= x11 <= (x1 + diff)),
        ((y0 - diff) <= y00 <= y11 <= (y1 + diff)),
    ))


def diff_mode(items: Numbers, max_diff: float = 2.0) -> Numbers:
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
    mode = modes(items)
    matched = [item for item in items if math.fabs(item - mode) <= max_diff]
    return matched


class Strategy(enum.Enum):
    LOWER = enum.auto()
    UPPER = enum.auto()
    LINEARISE = enum.auto()


def lookup(
        value: Number,
        table: typing.List,
        strategy: Strategy = None,
) -> Number:
    """Use table lookup to determine holy value.

    Out of Bounds:
    >>> lookup(0, [(10,10), (20, 30), (30, 0.5)])
    >>> lookup(40, [(10,10), (20, 30), (30, 0.5)])

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
    Returns:
        determined value
    """
    # TODO: VERY SLOW
    assert len(table) >= 2, f'invalid data table: {table}'
    if strategy is None:
        strategy = Strategy.LOWER
    if value < table[0][0]:
        return None
    if value > table[-1][0]:
        return None
    lower, result_lower = table[0]
    for upper, result_upper in table[1:]:
        if lower <= value <= upper:
            if strategy == Strategy.LINEARISE:
                diff = upper - lower
                mo = (result_upper - result_lower) / diff  # pylint:disable=C0103
                return result_lower + mo * (value - lower)
            if strategy == Strategy.LOWER:
                return result_lower
            return result_upper # if strategy == Strategy.UPPER: always upper
        lower, result_lower = upper, result_upper
    return None

def diffs(items: Numbers) -> Numbers:
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
