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
