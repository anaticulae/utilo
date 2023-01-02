# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib

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


def rtuple(start, end=None) -> tuple:
    """\
    >>> rtuple(10, 15)
    (10, 11, 12, 13, 14)
    """
    if end is None:
        start, end = 0, start
    return tuple(range(start, end))


def rlist(start, end=None) -> list:
    """\
    >>> rlist(5)
    [0, 1, 2, 3, 4]
    >>> rlist(5, 7)
    [5, 6]
    """
    return list(rtuple(start, end))


def ranges(start: float, stop: float, step: float = 1):
    """\
    >>> list(ranges(50, 90, 5))
    [50, 55, 60, 65, 70, 75, 80, 85, 90]
    """
    assert start <= stop
    assert step > 0

    while start <= stop:  # pylint:disable=W0149
        yield start
        start += step


def parse_tuple(
    raw: str,
    length: int = 4,
    typ=float,
    separator=' ',
    none: bool = False,
) -> tuple:
    """Convert `raw` to tuple of `typ`.

    If `length` is None the parsed tuple length is not verified.

    >>> parse_tuple('True false True False true', length=5, typ=bool)
    (True, False, True, False, True)
    >>> parse_tuple('9.0', length=1, typ=int)
    (9,)
    >>> parse_tuple('9.0 None', length=2, typ=int, none=True)
    (9, None)
    >>> parse_tuple('9.0 None', length=2, typ=int, none=False)
    Traceback (most recent call last):
    ...
    ValueError: could not convert string to float: 'None'
    >>> parse_tuple('504.02;316.08;547.52;390.24', separator=';')
    (504.02, 316.08, 547.52, 390.24)

    Ensure that big ints are converted properly.
    >>> parse_tuple('1 0 2 4144807557434719406', length=4, typ=int)
    (1, 0, 2, 4144807557434719406)
    """
    if typ is int:
        typ = utila.str2int
    if typ is bool:
        typ = utila.str2bool
    items = (typ(item) if not none or item != 'None' else None
             for item in raw.split(separator))
    if typ is float:
        items = utila.math.roundme(*items, convert=False, none=none)
    items = tuple(items)
    assert length is None or len(items) == length, f'could not parse {raw}'
    return items


def from_tuple(item: tuple, separator: str = ' ') -> str:
    """Convert tuple to str.

    >>> from_tuple((1.22, 5.0, 3))
    '1.22 5.0 3'
    >>> from_tuple((5, 6, 7), separator=', ')
    '5, 6, 7'
    """
    return separator.join(str(x) for x in item)


def update_tuple(data: tuple, value, index: int) -> tuple:
    """\
    >>> update_tuple((1, 2, 3, 4, 5), 5, 2)
    (1, 2, 5, 4, 5)
    >>> update_tuple((1, 2, 5), 3, 2)
    (1, 2, 3)
    >>> update_tuple((1, 2, 5), 10, 1)
    (1, 10, 5)
    """
    return (*data[0:index], value, *data[index + 1:])


def tuple_mult(items, value):
    """\
    >>> tuple_mult((4, 6, 10), 0.5)
    (2.0, 3.0, 5.0)
    """
    return tuple(item * value for item in items)


def tuple_plus(items, value):
    """\
    >>> tuple_plus((4, 6, 10), 5)
    (9, 11, 15)
    """
    return tuple(item + value for item in items)


def cstart(item) -> int:
    """\
    >>> cstart(10)
    10
    >>> cstart((5, 10))
    5
    """
    with contextlib.suppress(TypeError):
        return item[0]
    return item


def crange(item) -> tuple:
    """\
    >>> crange((5, 10))
    (5, 6, 7, 8, 9, 10)
    >>> crange(0)
    (0,)
    """
    with contextlib.suppress(TypeError):
        return rtuple(item[0], item[1] + 1)
    return (item,)
