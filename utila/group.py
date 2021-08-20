# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections

import utila


def groupby_none(items) -> list:
    """\
    >>> groupby_none([0, 1, 2, None, 1, None, 3, 4, 5, None])
    [(0, 1, 2), (1,), (3, 4, 5)]
    """
    result = []
    collected = []
    for item in items:
        if item is not None:
            collected.append(item)
        else:
            if collected:
                result.append(collected)
                collected = []
    if collected:
        result.append(collected)
    result = [tuple(item) for item in result]
    return result


def groupby_empty(items) -> list:
    """\
    >>> groupby_empty([[1, 2, 3], [4, 5], [ ], [6, 7, 9], [], []])
    [(1, 2, 3, 4, 5), (6, 7, 9)]
    """
    # convert to none to use `groupby_none`
    items = [None if not len(item) else item for item in items]  # pylint:disable=len-as-condition
    result = groupby_none(items)
    # merge neighbors
    result = [utila.flatten(item) for item in result]
    # ensure correct data type
    result = [tuple(item) for item in result]
    return result


def groupby_neighbors(items: list) -> list:
    """\
    >>> groupby_neighbors(([], [1, 2, 3], [], [], None, [5], [6], [7]))
    [[1, 2, 3], [5, 6, 7]]
    """
    if not items:
        return []
    result = []
    collected = []
    for item in items:
        if item not in (None, [], ''):
            collected.extend(item)
        else:
            if collected:
                result.append(collected)
                collected = []
    if collected:
        result.append(collected)
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


def groupby_diff(
    items: tuple,
    *,
    maxdiff: int = 1,
    selector: callable = None,
    sort: bool = True,
) -> list:
    """\
    >>> groupby_diff((1, 5, 2, 6, 9))
    [(1, 2), (5, 6), (9,)]
    >>> groupby_diff((5,))
    [(5,)]
    >>> groupby_diff([])
    []
    """
    assert maxdiff >= 0, f'negative maxdiff: {maxdiff}'
    if not items:
        return []
    selector = selector if selector else lambda x: x
    if sort:
        items = sorted(items, key=selector)
    result = [[items[0]]]
    for item in items[1:]:
        if (selector(item) - selector(result[-1][-1])) <= maxdiff:
            result[-1].append(item)
        else:
            result.append([item])
    result = [tuple(item) for item in result]
    return result


def groupby_x(items, selector: callable) -> list:
    """\
    >>> groupby_x('see he tee wee ge a b C'.split(), selector=len)
    [['see', 'tee', 'wee'], ['he', 'ge'], ['a', 'b', 'C']]
    """
    if not items:
        return []
    collected = collections.defaultdict(list)
    for item in items:
        collected[selector(item)].append(item)
    result = list(collected.values())
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


def xsome(items, count: 1, yield_rest: bool = True):
    """\
    >>> list(xsome([1, 2, 3, 5, 10, 12, 14], count=3))
    [[1, 2, 3], [5, 10, 12], [14]]
    """
    collected = []
    for item in items:
        collected.append(item)
        if len(collected) != count:
            continue
        yield collected
        collected = []
    if collected and yield_rest:
        yield collected
