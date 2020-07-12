# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

import utila


def near(first, second, diff: float = 2.0) -> bool:
    """Test that two items are close together.

    >>> near(2.1,-0.9, diff=3.0)
    True
    >>> near(1.0, 10, diff=1.0)
    False
    """
    return math.fabs(first - second) <= diff


def near_dims(item: tuple, dims: tuple, nears: tuple) -> bool:
    """\
    >>> near_dims((5, 5), [(4, 6), (4, 7), (10, 10)], [(1, 1), (1, 1), (0, 0)])
    0
    >>> near_dims((5, 5, 5),
    ...           dims=[(4, 6, 10), (4, 7, 30), (10, 10, 50)],
    ...           nears=[(1, 1, 0), (1, 1, 0), (5, 5, 45)])
    2
    >>> near_dims((5, 5), [(4,6), (4, 7)], [(0, 0), (0, 0)]) is None
    True
    """
    assert_equal_dim(item, dims)
    dims = list(dims)
    nears = list(nears)
    matches = utila.make_tuple(len(dims))
    for index, check in enumerate(item):
        if not dims:
            return None
        old_dims, dims = dims, []
        old_news, nears = nears, []
        old_matches, matches = matches, []
        for dim, near_, match in zip(old_dims, old_news, old_matches):
            if not utila.near(dim[index], check, near_[index]):
                continue
            dims.append(dim)
            nears.append(near_)
            matches.append(match)
    if matches:
        matches = matches[0] if len(matches) == 1 else matches
        return matches
    return None


def assert_equal_dim(item, dims) -> int:
    unique = {len(item) for item in dims}
    assert len(unique) == 1, str(unique)
    expected = unique.pop()
    assert len(item) == expected, f'{len(item)} != {expected}'
