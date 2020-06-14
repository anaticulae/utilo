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
