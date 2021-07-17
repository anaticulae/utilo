# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math
import operator
import typing

import utila

# x0, y0, x1, y1
Rectangle = typing.Tuple[float, float, float, float]
Rectangles = typing.List[Rectangle]


def rectangle_merge(rectangles: Rectangles) -> Rectangles:
    """Reduce list of rectangles to the minimal list to describe the
    covered area. Remove rectangle when there have a parent rectangle
    which covers them.

    Note: This algorithm does not determine the optimal count of
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


def rectangle_width(rectangle: Rectangle) -> float:
    """\
    >>> rectangle_width((5, 20, 40, 50))
    35
    """
    return utila.roundme(rectangle[2] - rectangle[0])


def rectangle_height(rectangle: Rectangle) -> float:
    """\
    >>> rectangle_height((15, 20, 40, 50))
    30
    """
    return utila.roundme(rectangle[3] - rectangle[1])


def rectangle_size(rectangle: Rectangle) -> float:
    """Determine area size of rectangle.

    >>> rectangle_size((50, 50, 100, 100))
    2500.0
    """
    width = rectangle_width(rectangle)
    height = rectangle_height(rectangle)
    area = math.fabs(width * height)
    area = utila.roundme(area)
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


def rectangle_scale(rectangle: tuple, scale: tuple):
    """\
    >>> rectangle_scale((20, 20, 60, 60), scale=(2.0, 2.0))
    (20, 20, 120.0, 120.0)
    >>> rectangle_scale((20, 20, 60, 60), scale=(2.0, 2.0, 2.0, 2.0))
    (40.0, 40.0, 120.0, 120.0)
    >>> rectangle_scale((20, 20, 60, 60), scale=(-3.0, -2.0, 2.0, 2.0))
    (-40.0, -20.0, 120.0, 120.0)
    """
    # x0, y0, x1, y1
    if len(scale) == 2:
        result = (
            rectangle[0],
            rectangle[1],
            rectangle[2] * scale[0],
            rectangle[3] * scale[1],
        )
    else:
        x00 = (scale[0] - 1.0) if scale[0] >= 0 else scale[0]
        y00 = (scale[1] - 1.0) if scale[1] >= 0 else scale[1]
        result = (
            rectangle[0] + rectangle[0] * x00,
            rectangle[1] + rectangle[1] * y00,
            rectangle[2] * scale[2],
            rectangle[3] * scale[3],
        )
    result = utila.roundme(result)
    return result


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
            if all((
                (x00 - diff) <= x0 <= x1 <= (x11 + diff),
                (y00 - diff) <= y0 <= y1 <= (y11 + diff),
            )):
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


def intersecting_rectangle(first: tuple, second: tuple) -> bool:
    """Check if two rectangles intersects at any point.

    Determine middle point of two rectangle and check if that middle
    point is inside of `first` or `second` rectangle.

    >>> intersecting_rectangle((0, 45, 55, 100), (45, 0, 55, 100))
    True
    >>> intersecting_rectangle((0, 0, 50, 50), (55, 55, 100, 100))
    False
    >>> intersecting_rectangle((0, 0, 50, 50), (0, 0, 50, 50)) # identical
    True
    """
    x = [first[0], first[2], second[0], second[2]]
    y = [first[1], first[3], second[1], second[3]]
    middle = sum(x) / 4, sum(y) / 4
    if dot_in_rectangle(first, middle):
        return True
    if dot_in_rectangle(second, middle):
        return True
    return False


def dot_in_rectangle(rectangle, dot) -> bool:
    x0, y0, x1, y1 = rectangle
    xx, yy = dot
    if xx < x0 or xx > x1:
        return False
    if yy < y0 or yy > y1:
        return False
    return True


def rectangle_border(rectangle: tuple):
    """Generator to run round trip on rectangle border.

    Visit: (left,top), (right, top), (right, bottom), (left, bottom), (left, top)

    >>> list(rectangle_border((0, 0, 55, 50)))
    [(0, 0, 55, 0), (55, 0, 55, 50), (0, 50, 55, 50), (0, 0, 0, 50)]

    Hint: Left coordinate is always smaller equal than right coordinate
    """
    x0, y0, x1, y1 = rectangle
    # left -> right
    yield (x0, y0, x1, y0)
    # right, top bottom
    yield (x1, y0, x1, y1)
    # right, right <- left
    yield (x0, y1, x1, y1)
    # left, bottom up
    yield (x0, y0, x0, y1)


def rectangle_border_points(rectangle: tuple):
    """Generator to run round trip on rectangle border.

    Visit: (left,top), (right, top), (right, bottom), (left, bottom)

    >>> list(rectangle_border_points((0, 0, 55, 50)))
    [(0, 0), (55, 0), (55, 50), (0, 50)]

    Hint: Left coordinate is always smaller equal than right coordinate
    """
    x0, y0, x1, y1 = rectangle
    yield x0, y0
    yield x1, y0
    yield x1, y1
    yield x0, y1


def rectangle_roundsmall(rectangle: Rectangle) -> Rectangle:
    """Round border in direction to the center of the rectangle to get a
    `smaller` rectangle which fit in more parent rectangles.

    >>> rectangle_roundsmall((5.596, 5.3360, 10.339, 10.222))
    (5.6, 5.34, 10.34, 10.22)
    """
    # round to move coordinate in center direction of page
    rounding = [
        math.ceil,  # x0
        math.ceil,  # y0
        math.floor,  # x1
        math.floor,  # y1
    ]
    result = [method(rectangle[index]) for index, method in enumerate(rounding)]
    # rounding to the middle can flip min and max. Therefore we have to
    # ensure x0/x1 and y0/y1 constraint.
    # TODO: VERY SMALL RECTANGLE?
    result = rectangle_ensure_bounding(rectangle)
    return tuple(result)


def rectangle_ensure_bounding(rectangle: Rectangle) -> Rectangle:
    """ensure x0/x1 and y0/y1 constraint."""
    result = (
        min(rectangle[0], rectangle[2]),
        min(rectangle[1], rectangle[3]),
        max(rectangle[0], rectangle[2]),
        max(rectangle[1], rectangle[3]),
    )
    return utila.roundme(result)


def rectangle_center(rectangle: Rectangle) -> tuple:
    """\
    >>> rectangle_center((20, 40, 100, 140))
    (60.0, 90.0)
    """
    center = (
        (rectangle[0] + rectangle[2]) / 2,
        (rectangle[1] + rectangle[3]) / 2,
    )
    center = utila.roundme(center)
    return center
