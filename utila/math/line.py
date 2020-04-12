# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

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
