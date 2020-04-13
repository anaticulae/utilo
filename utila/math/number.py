# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import typing

Number = typing.TypeVar('Number', int, float)  # pylint:disable=C0103
Numbers = typing.List[Number]  # pylint:disable=C0103

Floats = typing.List[float]
Ints = typing.List[int]


def numbers(items: typing.List) -> Numbers:
    """Convert iterable `items` to list of int's. Replace none
    convertable items to `None`.

    Args:
        items: iterable with items to convert
    Returns:
        List of int's or None's.

    >>> numbers(['1', '3', '5', 'wasd'])
    [1, 3, 5, None]
    """
    result = []
    for item in items:
        try:
            result.append(int(item))
        except ValueError:
            result.append(None)
    return result
