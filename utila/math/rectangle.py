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


def rectangle_max(items: list) -> tuple:
    """\
    >>> rectangle_max(((-20, 0, 100, 100), (50, 50, 120, 124)))
    (-20, 0, 120, 124)
    """
    assert items, 'no rectangles given'
    x0 = utila.mins(item[0] for item in items)
    x1 = utila.maxs(item[2] for item in items)
    y0 = utila.mins(item[1] for item in items)
    y1 = utila.maxs(item[3] for item in items)
    return x0, y0, x1, y1


class RectangleCheck:
    """Verify if a rectangle is inside a group of rectangles.

    >>> check = RectangleCheck()
    >>> check.extend(50, 50, 100, 100)
    >>> check.extend(0, 0, 50, 100)
    >>> check.shrink()
    >>> assert check.contains(25, 25, 50, 50)
    >>> assert check.contains(75, 75, 100, 100)
    >>> assert not check.contains(100, 100, 150, 150)
    """

    def __init__(self, max_diff: float = 0.0):
        self.max_diff = max_diff
        self.content = []

    def extend(self, x0, y0, x1, y1):
        self.content.append((x0, y0, x1, y1))

    def contains(self, x0, y0, x1, y1) -> bool:
        diff = self.max_diff / 2
        for x00, y00, x11, y11 in self.content:
            if all(((x00 - diff) <= x0 <= x1 <= (x11 + diff),
                    (y00 - diff) <= y0 <= y1 <= (y11 + diff))):
                return True
        return False

    def shrink(self):
        """Reduce checking rectangles to minimal required. Remove
        rectangle is there are included in a parent rectangle."""
        self.content = rectangle_merge(self.content)

    def __getitem__(self, index):
        return self.content[index]

    def __len__(self):
        return len(self.content)


def sort_leftright_topdown(items):
    """Sort top down by y1 component.

    >>> sort_leftright_topdown([(0, 0, 50, 50), (20, 20, 40, 40), (-50, -10, 0, 40)])
    [(-50, -10, 0, 40), (20, 20, 40, 40), (0, 0, 50, 50)]
    """
    # left to right
    items = sorted(items, key=operator.itemgetter(0))
    # top down
    items = sorted(items, key=operator.itemgetter(3))
    return items


def sort_leftright_topdown_upper(items):
    """Sort top down by y0 component.

    >>> sort_leftright_topdown_upper([(0, 0, 50, 50), (20, 20, 40, 40), (-50, -10, 0, 40)])
    [(-50, -10, 0, 40), (0, 0, 50, 50), (20, 20, 40, 40)]
    """
    # left to right
    items = sorted(items, key=operator.itemgetter(0))
    # top down
    items = sorted(items, key=operator.itemgetter(1))
    return items
