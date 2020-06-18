# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


def groupby_none(items):
    """\
    >>> groupby_none([1, 2, None, 1, None, 3, 4, 5, None])
    [(1, 2), (1,), (3, 4, 5)]
    """
    result = []
    collected = []
    for item in items:
        if item:
            collected.append(item)
        else:
            if collected:
                result.append(tuple(collected))
                collected = []
    if collected:
        result.append(tuple(collected))
    return result


def groupby_ascending(items) -> int:
    """\
    >>> groupby_ascending([1, 2, 3, 0, 1, 2, 3, 4, 0, 1])
    [(1, 2, 3), (0, 1, 2, 3, 4), (0, 1)]
    """
    if not items:
        return 0
    result = [[items[0]]]
    for item in items[1:]:
        if item < result[-1][-1]:
            result.append([item])
        else:
            result[-1].append(item)
    return [tuple(item) for item in result]


def groupby_diff(pages: tuple, *, diff=1) -> list:
    """\
    >>> groupby_diff((1, 5, 2, 6, 9))
    [(1, 2), (5, 6), (9,)]
    >>> groupby_diff(None)
    [None]
    >>> groupby_diff((5,))
    [(5,)]
    """
    assert diff >= 0, 'negative diff'
    if not pages:
        return [None]
    pages = sorted(pages)
    result = [[pages[0]]]
    for item in pages[1:]:
        if item - result[-1][-1] <= diff:
            result[-1].append(item)
        else:
            result.append([item])
    result = [tuple(item) for item in result]
    return result


def longest(items, number: int = 1):
    """\
    >>> longest([(1, 2, 4), (2, 2, 2, 2), (5, 5, 5)])
    (2, 2, 2, 2)
    >>> longest([(1, 2, 4), (2, 2, 2, 2), (5, 5, 5)], number=3)
    [(2, 2, 2, 2), (1, 2, 4), (5, 5, 5)]
    """
    if not items:
        return []
    items = sorted(items, key=len, reverse=True)
    if number == 1:
        return items[0]
    return items[0:number]


def shortest(items, number: int = 1):
    """\
    >>> shortest([(1, 2, 4), (2, 2, 2, 2), (5, 5, 5)])
    (1, 2, 4)
    >>> shortest([(1, 2, 4), (2, 2, 2, 2), (5, 5, 5)], number=2)
    [(1, 2, 4), (5, 5, 5)]
    """
    assert number >= 1, 'invalid number'
    if not items:
        return []
    items = sorted(items, key=len)
    if number == 1:
        return items[0]
    return items[0:number]
