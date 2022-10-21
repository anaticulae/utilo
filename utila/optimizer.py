# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def zip_optimizer(first, second, *, selector=None):
    """\
    >>> zip_optimizer(((0, 1, 2), (6, 7, 8), (11, 12, 13, 14)),
    ...  ((4, 5, 6, 7, 8, 9, 10, 11),),
    ... )
    [(0, 1, 2), (4, 5, 6, 7, 8, 9, 10, 11)]
    >>> zip_optimizer(((0, 1), (4, 5), (8, 9)),
    ...  ((3, 4, 5),),
    ... )
    [(0, 1), (3, 4, 5), (8, 9)]
    >>> zip_optimizer(((0, 1), (4, 5)),
    ... ((2, 3), (6, 7, 8))
    ... )
    [(0, 1), (2, 3), (4, 5), (6, 7, 8)]
    """
    selector = utila.scall_or_me(selector)
    result = list(first)
    current = score_area(selector(item) for item in result)
    for todo in second:
        new = tryit(result, todo, selector)
        scored = score_area([selector(item) for item in new])
        if scored > current:
            result = new
            current = scored
    return result


def tryit(items, test, selector):
    result = [test]
    for item in items:
        if unique(selector(item), selector(test)):
            result.append(item)
    result.sort(key=lambda x: selector(x)[0])  # pylint:disable=C3001
    return result


def unique(first, second):
    mixed = []
    for item in first:
        mixed.append(item)
    for item in second:
        mixed.append(item)
    mixed = utila.make_unique(mixed)
    expected = len(first) + len(second)
    return len(mixed) == expected


def score_area(area):
    """\
    >>> score_area([(17, 18, 19, ), (0, 1, 2, 3), (0, 1, 2, 3)])
    11
    >>> score_area([0, 1, 2, 3])
    4
    """
    try:
        flat = utila.flat(area)
    except TypeError:
        flat = area
    return len(flat)
