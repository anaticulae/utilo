# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

import utila
import utila.math.const
import utila.math.distance


def length(x0, y0, x1, y1) -> float:
    return utila.math.distance.norm(x0, y0, x1, y1)


def round_line(x0, y0, x1, y1, max_noise=4.0) -> tuple:
    """Ensure that a nearly horizontal or vertical line contains no noise.

    >>> round_line(*(10.9, 100, 9.8, 200))
    (10.4, 100, 10.4, 200)
    """
    if math.fabs(x0 - x1) < max_noise:
        x1 = (x1 + x0) / 2
        x0 = x1
    if math.fabs(y0 - y1) < max_noise:
        y1 = (y1 + y0) / 2
        y0 = y1
    x0, y0, x1, y1 = utila.roundme(x0, y0, x1, y1, digits=1)
    return (x0, y0, x1, y1)


def unique_lines(lines: list, *, max_diff: float = 3.0) -> list:
    """\
    >>> unique_lines(((50, 50, 100, 100), (50, 50, 100, 100), (0, 0, 5, 5)))
    [(50, 50, 100, 100), (0, 0, 5, 5)]
    """
    result = []
    for item in lines:
        if any((equal_lines(item, it, max_diff=max_diff) for it in result)):
            continue
        result.append(item)
    return result


def equal_lines(first, second, max_diff: float = 3.0) -> bool:
    """Check if `first` and `second` are equal.

    >>> equal_lines((10, 10, 100, 10), (11, 10, 99, 10))
    True
    """
    if length(first[0], first[1], second[0], second[1]) > max_diff:
        return False
    if length(first[2], first[3], second[2], second[3]) > max_diff:
        return False
    return True


def isdot(item, max_length=3.0) -> bool:
    """Check if `item` is a very short `max_length` line which can be
    interpreted as a dot.

    >>> isdot((10, 10, 11, 11))
    True
    """
    return length(*item) <= max_length


class IndenticalLineError(ValueError):
    pass


def intersecting_lines(first, second, max_diff=0.0):  # pylint:disable=R1260,R0914,R0912
    """Check if two lines intersects with each other.

    >>> intersecting_lines((0, 0, 100,100), (0, 100, 100, 0))
    (50.0, 50.0)
    >>> not intersecting_lines((0, 0, 100,0), (0, 100, 100, 100))
    True
    >>> intersecting_lines((0, 0, 0, 100), (0, 100, 100, 100))
    (0.0, 100.0)
    >>> not intersecting_lines((0, 100, 100, 100), (0, 0, 50, 50))
    True
    >>> not intersecting_lines((0, 100, 100, 100), (0, 200, 100, 200)) # two horizontal lines
    True
    """
    if utila.iszero(length(*first)) or utila.iszero(length(*second)):
        raise ValueError(f"it's not a line it's a dot {first}; {second}")

    # disable short math names
    # pylint:disable=C0103
    x0, y0, x1, y1 = first
    x00, y00, x11, y11 = second

    try:
        m0 = (x0 - x1) / (y0 - y1)
    except ZeroDivisionError:
        m0 = 0.0
    try:
        m1 = (x00 - x11) / (y00 - y11)
    except ZeroDivisionError:
        m1 = 0.0

    if utila.iszero(x0 - x1):
        m0 = utila.math.const.NEAR_INF
    if utila.iszero(x00 - x11):
        m1 = utila.math.const.NEAR_INF

    n0 = y0 - m0 * x0
    n1 = y00 - m1 * x00

    x0, x1 = min([x0, x1]), max([x0, x1])
    y0, y1 = min([y0, y1]), max([y0, y1])
    x00, x11 = min([x00, x11]), max([x00, x11])
    y00, y11 = min([y00, y11]), max([y00, y11])

    if utila.iszero(n0 - n1) and utila.iszero(m0 - m1):
        if y0 == y00 and y1 == y11:
            raise IndenticalLineError(f'identical lines {first} {second}')

    if m0 == m1 and not utila.isinf(m0):
        # 2 never matching lines
        return None
    try:
        xmatch = (n1 + n0) / (m0 - m1)
    except ZeroDivisionError:
        xmatch = None

    if not xmatch:
        if max_diff:
            potential = [
                (x0, y0, x00, y00),
                (x0, y0, x11, y11),
                (x1, y1, x00, y00),
                (x1, y1, x11, y11),
            ]
            for item in potential:
                if length(*item) < max_diff:
                    return (item[0], item[1])
        return None

    ymatch = xmatch * m0 + n0
    xmatch = utila.roundme(xmatch)

    inside = all([
        -max_diff / 2 + x0 <= xmatch <= x1 + max_diff / 2,
        -max_diff / 2 + x00 <= xmatch <= x11 + max_diff / 2,
        -max_diff / 2 + y0 <= ymatch <= y1 + max_diff / 2,
        -max_diff / 2 + y00 <= ymatch <= y11 + max_diff / 2,
    ])
    if not inside:
        return None

    return xmatch, ymatch
