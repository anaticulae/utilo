# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def make_tuple(length: int, *, start: int = 0) -> tuple:
    """Create tuple of `length` with starting point `start`.

    >>> make_tuple(5)
    (0, 1, 2, 3, 4)
    >>> make_tuple(3, start=10)
    (10, 11, 12)
    """
    assert length > 0, 'require positive length'
    return tuple(index + start for index in range(length))


def ranged_tuple(start, end) -> tuple:
    """\
    >>> ranged_tuple(10, 15)
    (10, 11, 12, 13, 14)
    """
    if end is None:
        start, end = 0, start
    return tuple(range(start, end))


def ranged_list(start, end=None) -> tuple:
    """\
    >>> ranged_list(5)
    [0, 1, 2, 3, 4]
    >>> ranged_list(5, 7)
    [5, 6]
    """
    return list(ranged_tuple(start, end))


def ranges(start: float, stop: float, step: float):
    """\
    >>> list(ranges(50, 90, 5))
    [50, 55, 60, 65, 70, 75, 80, 85, 90]
    """
    assert start <= stop
    assert step > 0

    while start <= stop:
        yield start
        start += step


def parse_tuple(raw: str, length: int = 4, typ=float) -> tuple:
    """Convert `raw` to tuple of `typ`.

    >>> parse_tuple('True false True False true', length=5, typ=bool)
    (True, False, True, False, True)
    """
    if typ is int:
        typ = utila.str2int
    if typ is bool:
        typ = utila.str2bool
    items = (typ(item) for item in raw.split())
    if typ is float:
        items = utila.math.roundme(*items)
    items = tuple(items)
    assert len(items) == length, f'could not parse {raw}'
    return items


def from_tuple(item: tuple, separator: str = ' ') -> str:
    """Convert tuple to str.

    >>> from_tuple((1.22, 5.0, 3))
    '1.22 5.0 3'
    >>> from_tuple((5, 6, 7), separator=', ')
    '5, 6, 7'
    """
    return separator.join(str(x) for x in item)
