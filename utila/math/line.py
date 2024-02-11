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


def length(x0, y0, x1, y1) -> float:
    return utila.norm(x0, y0, x1, y1)


def round_line(x0, y0, x1, y1, digits: int = 1, max_noise=4.0) -> tuple:
    """Ensure that a nearly horizontal or vertical line contains no noise.

    >>> round_line(*(10.9, 100, 9.8, 200))
    (10.4, 100, 10.4, 200)
    >>> round_line(*(10.9, 100, 28, 200))
    (10.9, 100, 28, 200)
    >>> round_line(10, 10.5, 200, 11)
    (10, 10.8, 200, 10.8)
    """
    if math.fabs(x0 - x1) < max_noise:
        x1 = (x1 + x0) / 2
        x0 = x1
    if math.fabs(y0 - y1) < max_noise:
        y1 = (y1 + y0) / 2
        y0 = y1
    x0, y0, x1, y1 = utila.roundme(x0, y0, x1, y1, digits=digits)
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
    >>> equal_lines((0, 10, 100, 10), (11, 10, 99, 10))
    False
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
    (-0.0, 100.0)
    >>> not intersecting_lines((0, 100, 100, 100), (0, 0, 50, 50))
    True
    >>> not intersecting_lines((0, 100, 100, 100), (0, 200, 100, 200)) # two horizontal lines
    True
    """
    # disable short math names
    # pylint:disable=C0103
    maxdiff = max_diff / 2
    x0, y0, x1, y1 = first
    x00, y00, x11, y11 = second

    if x0 < x1 + maxdiff < x00 < x11 or x00 < x11 + maxdiff < x0 < x1:
        # no possible intersection
        return None
    if y0 < (y1 + maxdiff) < y00 < y11 or y00 < (y11 + maxdiff) < y0 < y1:
        # no possible intersection
        return None

    # if utila.iszero(length(*first)) or utila.iszero(length(*second)):
    #     raise ValueError(f"it's not a line it's a dot {first}; {second}")

    x1, x2, x3, x4 = x0, x1, x00, x11
    y1, y2, y3, y4 = y0, y1, y00, y11

    x1x2 = x1 - x2
    x3x4 = x3 - x4
    y1y2 = y1 - y2
    y3y4 = y3 - y4
    # D = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    d = (x1x2) * (y3y4) - (y1y2) * (x3x4)
    if utila.iszero(d):
        matched = matching_endings(first, second, maxdiff=maxdiff)
        if matched:
            return matched
        if utila.isequal(first[1], second[1]) and utila.isequal(first[3], second[3]): # yapf:disable
            raise IndenticalLineError(f'identical lines {first} {second}')
        return None
    # Px = ((x1 * y2 - y1 * x2) * (x3x4) - (x1x2) * (x3 * y4 - y3 * x4)) / D
    # Py = ((x1 * y2 - y1 * x2) * (y3y4) - (y1y2) * (x3 * y4 - y3 * x4)) / D
    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4
    px = (a * (x3x4) - (x1x2) * b) / d
    py = (a * (y3y4) - (y1y2) * b) / d

    if utila.isoutside(px, first[0], first[2], maxdiff=maxdiff) or\
       utila.isoutside(px, second[0], second[2], maxdiff=maxdiff) or\
       utila.isoutside(py, first[1], first[3], maxdiff=maxdiff) or\
       utila.isoutside(py, second[1], second[3], maxdiff=maxdiff):
        return None
    return px, py


def matching_endings(first, second, maxdiff):
    x1, y1, x2, y2 = first
    x3, y3, x4, y4 = second
    if length(x1, y1, x3, y3) < maxdiff:
        return (x1, y1)
    if length(x1, y1, x4, y4) < maxdiff:
        return (x1, y1)
    if length(x2, y2, x3, y3) < maxdiff:
        return (x2, y2)
    if length(x2, y2, x4, y4) < maxdiff:
        return (x2, y2)
    return None


def intersecting_ending(first: tuple, second: tuple, tol: float = 3.0) -> bool:
    """Check if start or end point of two line intersects.

    >>> intersecting_ending((0, 0, 100, 0), (100, 0, 100, 100))
    True
    >>> intersecting_ending((33, 33, 66, 66), (66, 66, 33, 33)) is None
    True
    >>> intersecting_ending((15.0, 15.0, 30.0, 30.0), (-15.0, -15.0, -30.0, -30.0))
    False

    Args:
        first(BoundingBox): line(x0, y0, x1, y1)
        second(BoundingBox): line(x0, y0, x1, y1)
        tol(float): max distance of two matching points
    Returns:
        None  if both lines are equal
        False if nothing matches
        True  if least one element matches
    """
    # Check only if points intersects
    x0, y0, x2, y2 = first
    x1, y1, x3, y3 = second

    first_distance = min(length(x0, y0, x1, y1), length(x0, y0, x3, y3))
    second_distance = min(length(x2, y2, x3, y3), length(x2, y2, x1, y1))

    if first_distance < 0.00001 and second_distance < 0.00001:
        # intersecting with themselves
        return None

    if first_distance <= tol:
        return True

    if second_distance <= tol:
        return True

    return False


def merge_lines(items, diff: float = 3.0):
    """Some pdf printer prints long lines as a couple of short lines.
    For analysis it is required, that these lines are merged to single
    lines to work with correct length and position.

    This algorithm merges lines which are:
     - connected in two points
     - have the same raising.

    As a requirement, the lines are sorted top down and left right.

    >>> merge_lines([(328.18, 373.08, 329.68, 373.83),
    ...              (329.68, 373.08, 416.03, 373.83),
    ...              (416.02, 373.08, 416.77, 373.83),
    ...              (416.77, 373.08, 502.39, 373.83),
    ...              (502.40, 373.08, 504.65, 373.83),])
    [(328.18, 373.08, 504.65, 373.83)]

    >>> merge_lines([(257.58, 440.65 ,259.08 ,442.15),
    ...              (259.08, 440.65 ,328.18 ,442.15),
    ...              (328.18, 440.65 ,329.68 ,442.15),
    ...              (329.68, 440.65 ,416.03 ,441.40),
    ...              (416.02, 440.65 ,416.77 ,442.15),
    ...              (416.77, 440.65 ,502.39 ,441.40),
    ...              (502.40, 440.65 ,504.65 ,442.15)])
    [(257.58, 440.65, 504.65, 442.15)]
    """
    if not items:
        return []
    result = [items[0]]
    for item in items[1:]:
        last_x1, last_y1 = result[-1][2], result[-1][3]
        x0, y0 = item[0], item[1]
        if not all((
                utila.near(last_x1, x0, diff=diff),
                utila.near(last_y1, y0, diff=diff),
                utila.near(
                    line_raising(item, diff),
                    line_raising(result[-1], diff),
                    diff=diff,
                ),
        )):
            result.append(item)
        else:
            # unite
            new = (result[-1][0], result[-1][1], item[2], item[3])
            result.pop()
            result.append(new)

    # sort item top down; left right after merging
    result = sorted(result, key=operator.itemgetter(1, 0))
    return result


def line_raising(item, diff=1.0) -> float:
    """\
    >>> line_raising((0, 0, 50, 50))
    1.0
    >>> line_raising((0, 0, 0, 100)) # inf line_raising
    2147483647
    """
    xdiff = (item[2] - item[0])
    ydiff = (item[3] - item[1])
    if -diff <= ydiff <= diff:
        return 0.0
    if -diff <= xdiff <= diff:
        return utila.INF
    return xdiff / ydiff
