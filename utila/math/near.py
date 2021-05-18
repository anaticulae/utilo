# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import itertools

import utila


def near(current, expected, diff: float = 2.0, none: bool = False) -> bool:
    """Test that two items are close together.

    >>> near(2.1,-0.9, diff=3.0)
    True
    >>> near(1.0, 10, diff=1.0)
    False
    >>> near(None, None, none=True)
    True
    >>> near(None, None, none=False)
    Traceback (most recent call last):
        ...
    TypeError: ...
    """
    try:
        return expected - diff <= current <= expected + diff
    except TypeError as error:
        if not none:
            raise error from None
    return current == expected


def nears(currents, expects, diff: float = 2.0, none: bool = False) -> bool:
    """Test that two n-items are close together.

    >>> nears((1, 2, 3), (0.5, 1.5, 3.5), diff=0.5)
    True
    >>> nears((1, 2), (0.5, 1.5), diff=0.3)
    False
    >>> nears((5, 2), (6, 4), diff=(1, 2))
    True
    >>> nears((5, 2), (6, 4), diff=1)
    False
    """
    diffs = itertools.cycle((diff,)) if isinstance(diff, (int, float)) else diff
    result = (utila.near(expect, current, diff=diff, none=none)
              for expect, current, diff in zip(expects, currents, diffs))
    return all(result)


def pnear(
    reference,
    current,
    rel_tol: float = 0.0,
    abs_tol: float = 0.05,
) -> bool:
    """\
    >>> pnear(10, 8, 0.2)
    True
    >>> pnear(10, 8, 0.19)
    False
    >>> pnear(0, 0.1, rel_tol=0.02, abs_tol=0.1)
    True
    """
    # TODO: UNIT WITH NEAR?
    lower = reference * (1 - rel_tol)
    upper = reference * (1 + rel_tol)
    if lower <= current <= upper:
        return True
    lower = reference - abs_tol
    upper = reference + abs_tol
    if lower <= current <= upper:
        return True
    return False


def near_dims(
    item: tuple,
    dims: tuple,
    diffs: tuple,
    allow_none: bool = False,
) -> bool:
    """\
    >>> near_dims((5, 5), [(4, 6), (4, 7), (10, 10)], [(1, 1), (1, 1), (0, 0)])
    0
    >>> near_dims((5, 5, 5),
    ...           dims=[(4, 6, 10), (4, 7, 30), (10, 10, 50)],
    ...           diffs=[(1, 1, 0), (1, 1, 0), (5, 5, 45)])
    2
    >>> near_dims((5, 5), [(4,6), (4, 7)], [(0, 0), (0, 0)]) is None
    True
    """
    assert_equal_dim(item, dims)
    dims = list(dims)
    diffs = list(diffs)
    matches = utila.make_tuple(len(dims))
    for index, check in enumerate(item):
        if not dims:
            return None
        old_dims, dims = dims, []
        old_news, diffs = diffs, []
        old_matches, matches = matches, []
        for dim, near_, match in zip(old_dims, old_news, old_matches):
            if dim[index] is None or check is None and allow_none:
                # None item always pass the test
                pass
            elif not utila.near(dim[index], check, near_[index]):
                continue
            dims.append(dim)
            diffs.append(near_)
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
