# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math
import operator

import utila

# x0, y0, x1, y1
Rectangle = tuple[float, float, float, float]
Rectangles = list[Rectangle]


def rect_merge(rectangles: Rectangles) -> Rectangles:
    """Reduce list of rectangles to the minimal list to describe the
    covered area. Remove rectangle when there have a parent rectangle
    which covers them.

    Note: This algorithm does not determine the optimal count of
    rectangles, if two rectangle cover the area of a third one, all
    three rectangle will be saved.

    >>> rect_merge([(50, 50, 100, 100), (20, 20, 100, 100)])
    [(20, 20, 100, 100)]
    >>> rect_merge([(50, 50, 100, 100), (100, 100, 150, 150)])
    [(50, 50, 100, 100), (100, 100, 150, 150)]
    >>> assert rect_merge([]) is None
    """
    if not rectangles:
        return None

    def merge(items):
        # sort top down, left right
        items = sorted(items, key=operator.itemgetter(1, 0))
        result = []
        while len(items) >= 2:  # pylint:disable=W0149
            item = items.pop()
            if any((rect_inside(check, item) for check in items)):
                continue
            result.insert(0, item)
        result.insert(0, items.pop())
        return result

    current = rectangles[:]
    merged = merge(current)
    while merged != current:  # pylint:disable=W0149
        # repeat till algorithm does not change the list
        current = merged
        merged = merge(current)
    return current


def rect_width(rectangle: Rectangle) -> float:
    """\
    >>> rect_width((5, 20, 40, 50))
    35
    """
    return utila.roundme(rectangle[2] - rectangle[0])


def rect_height(rectangle: Rectangle) -> float:
    """\
    >>> rect_height((15, 20, 40, 50))
    30
    """
    return utila.roundme(rectangle[3] - rectangle[1])


def rect_size(rectangle: Rectangle) -> float:
    """Determine area size of rectangle.

    >>> rect_size((50, 50, 100, 100))
    2500.0
    """
    width = rect_width(rectangle)
    height = rect_height(rectangle)
    area = math.fabs(width * height)
    area = utila.roundme(area)
    return area


def rect_inside(first, second, diff: float = 0):
    """Is `second` rectangle in `first`.

    >>> rect_inside((0, 0, 100, 100), (50, 50, 100, 100))
    True
    >>> rect_inside((0, 0, 100, 100), (75, 75, 125, 125))
    False
    """
    diff = diff / 2
    x0, y0, x1, y1 = first
    x00, y00, x11, y11 = second
    return all((
        ((x0 - diff) <= x00 <= x11 <= (x1 + diff)),
        ((y0 - diff) <= y00 <= y11 <= (y1 + diff)),
    ))


def rect_max(items: list) -> tuple:
    """\
    >>> rect_max(((-20, 0, 100, 100), (50, 50, 120, 124)))
    (-20, 0, 120, 124)
    """
    assert items, 'no rectangles given'
    x0 = utila.mins(item[0] for item in items)
    x1 = utila.maxs(item[2] for item in items)
    y0 = utila.mins(item[1] for item in items)
    y1 = utila.maxs(item[3] for item in items)
    return x0, y0, x1, y1


def rect_scale(rectangle: tuple, scale: tuple):
    """\
    >>> rect_scale((20, 20, 60, 60), scale=(2.0, 2.0))
    (20, 20, 120.0, 120.0)
    >>> rect_scale((20, 20, 60, 60), scale=(2.0, 2.0, 2.0, 2.0))
    (40.0, 40.0, 120.0, 120.0)
    >>> rect_scale((20, 20, 60, 60), scale=(-3.0, -2.0, 2.0, 2.0))
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
    >>> len(check)
    2
    >>> check[1]
    (50, 50, 100, 100)
    >>> list(RectangleCheck(max_diff=10))
    []
    """

    def __init__(self, diff_max: float = 0.0, max_diff: float = None):
        if max_diff is not None:
            diff_max = max_diff
        self.diff_max = diff_max
        self.content = []

    def extend(self, x0, y0, x1, y1):
        self.content.append((x0, y0, x1, y1))

    def contains(self, x0, y0, x1, y1) -> bool:
        diff = self.diff_max / 2
        for x00, y00, x11, y11 in self.content:  # pylint:disable=C0501
            if all((
                (x00 - diff) <= x0 <= x1 <= (x11 + diff),
                (y00 - diff) <= y0 <= y1 <= (y11 + diff),
            )):
                return True
        return False

    def shrink(self):
        """Reduce checking rectangles to minimal required.

        Remove rectangle which are included in a parent rectangle.
        """
        self.content = rect_merge(self.content)

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


def rect_intersecting(first: tuple, second: tuple) -> bool:
    """Check if two rectangles intersects at any point.

    Iterate over border points and check if border point is inside the
    other rectangle.

    >>> rect_intersecting((0, 45, 55, 100), (45, 0, 55, 100))
    True
    >>> rect_intersecting((0, 0, 50, 50), (55, 55, 100, 100))
    False
    >>> rect_intersecting((0, 0, 50, 50), (0, 0, 50, 50)) # identical
    True
    >>> rect_intersecting((99.11, 112.15, 496.16, 272.75), (195.33, 296.66, 399.95, 321.37))
    False
    """
    for point in rect_border_points(first):
        if not dot_in_rectangle(second, point):
            continue
        return True
    for point in rect_border_points(second):
        if not dot_in_rectangle(first, point):
            continue
        return True
    return False


def rectangles_intersecting(
    rectangles: Rectangles,
    test: Rectangle,
) -> bool:
    """\
    >>> rectangles_intersecting(test=(20, 20, 30, 30), rectangles=[(10, 10, 40, 40)])
    True
    """
    return any(utila.rect_intersecting(item, test) for item in rectangles)


def dot_in_rectangle(rectangle, dot) -> bool:
    x0, y0, x1, y1 = rectangle
    xx, yy = dot
    if xx < x0 or xx > x1:
        return False
    if yy < y0 or yy > y1:
        return False
    return True


def rect_border(rectangle: tuple):
    """Generator to run round trip on rectangle border.

    Visit: (left,top), (right, top), (right, bottom), (left, bottom), (left, top)

    >>> list(rect_border((0, 0, 55, 50)))
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


def rect_border_points(rectangle: tuple):
    """Generator to run round trip on rectangle border.

    Visit: (left,top), (right, top), (right, bottom), (left, bottom)

    >>> list(rect_border_points((0, 0, 55, 50)))
    [(0, 0), (55, 0), (55, 50), (0, 50)]

    Hint: Left coordinate is always smaller equal than right coordinate
    """
    x0, y0, x1, y1 = rectangle
    yield x0, y0
    yield x1, y0
    yield x1, y1
    yield x0, y1


def rect_roundsmall(rectangle: Rectangle) -> Rectangle:
    """Round border in direction to the center of the rectangle to get a
    `smaller` rectangle which fit in more parent rectangles.

    >>> rect_roundsmall((5.596, 5.3360, 10.339, 10.222))
    (5.6, 5.34, 10.33, 10.22)
    """
    # round to move coordinate in center direction of page
    rounding = [
        math.ceil,  # x0
        math.ceil,  # y0
        math.floor,  # x1
        math.floor,  # y1
    ]
    result = [
        method(rectangle[index] * 100.0) / 100.0
        for index, method in enumerate(rounding)
    ]
    # rounding to the middle can flip min and max. Therefore we have to
    # ensure x0/x1 and y0/y1 constraint.
    # TODO: VERY SMALL RECTANGLE?
    result = rect_ensure_bounding(result)
    return result


def rect_ensure_bounding(rectangle: Rectangle) -> Rectangle:
    """ensure x0/x1 and y0/y1 constraint."""
    result = (
        min(rectangle[0], rectangle[2]),
        min(rectangle[1], rectangle[3]),
        max(rectangle[0], rectangle[2]),
        max(rectangle[1], rectangle[3]),
    )
    return utila.roundme(result)


def rect_center(rectangle: Rectangle) -> tuple:
    """\
    >>> rect_center((20, 40, 100, 140))
    (60.0, 90.0)
    """
    center = (
        (rectangle[0] + rectangle[2]) / 2,
        (rectangle[1] + rectangle[3]) / 2,
    )
    center = utila.roundme(center)
    return center


def rect_overlapping(
    master: Rectangle,
    test: Rectangle,
    *,
    returnsize: bool = False,
) -> float:
    """\
    >>> rect_overlapping((0, 0, 50, 50), (10, 10, 40, 40), returnsize=True)
    (1.0, 900.0)
    >>> rect_overlapping((0, 0, 50, 50), (55, 55, 100, 100))
    0.0
    >>> rect_overlapping((0, 0, 50, 50), (0, 25, 50, 75))
    0.5
    >>> rect_overlapping((0, 0, 50, 50), (25, 25, 75, 75))
    0.25
    >>> rect_overlapping((0, 0, 30, 30), (0, 20, 30, 50))
    0.33
    >>> rect_overlapping((0, 0, 30, 30), (15, 20, 30, 50))
    0.33
    >>> rect_overlapping((10, 10, 30, 30), (25, 20, 30, 40))
    0.5
    >>> rect_overlapping((10, 10, 30, 30), (29.9999, 30, 50, 50))  # check if not size
    0.0

    Determine overlapping rate for horizonals
    >>> rect_overlapping((92.13, 425.58, 499.79, 514.99), (92.13, 425.58, 499.79, 425.58))
    1.0
    """
    if not rect_intersecting(master, test):
        return 0.0
    if not rect_height(test):
        # increase test rectangle to enable matching horizontal lines
        master = (master[0] - 0.01, master[1] - 0.01, master[2] + 0.01,
                  master[3] + 0.01)
        test = (test[0] - 0.01, test[1] - 0.01, test[2] + 0.01, test[3] + 0.01)
    ymin = max(master[1], test[1])
    ymax = min(master[3], test[3])
    ymin, ymax = sorted((ymin, ymax))
    xmin = max(master[0], test[0])
    xmax = min(master[2], test[2])
    xmin, xmax = sorted((xmin, xmax))
    intersecting = (xmin, ymin, xmax, ymax)
    intersecting_size = utila.rect_size(intersecting)
    if not intersecting_size:
        return 0.0
    size_test = utila.rect_size(test)
    rate = intersecting_size / size_test
    rate = utila.roundme(rate)
    if returnsize:
        return rate, intersecting_size
    return rate
