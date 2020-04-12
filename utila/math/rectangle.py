# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math
import operator
import typing

import utila.math

# x0, y0, x1, y1
Rectangle = typing.Tuple[float, float, float, float]
Rectangles = typing.List[Rectangle]


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
    area = utila.math.roundme(area)
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
