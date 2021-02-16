# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import enum
import re

import utila


def str2int(item: str, default=None) -> int:
    """\
    >>> str2int('10')
    10
    >>> str2int('1.3')
    1
    >>> str2int('ABC', default=13)
    13
    """
    item = str2float(item, default=default)
    return item if item is None else int(item)


def str2float(item: str, default=None) -> float:
    """\
    >>> str2float('10')
    10.0
    >>> str2float('1.3')
    1.3
    >>> str2float('ABC', default=13)
    13
    """
    try:
        return float(item)
    except ValueError as error:
        if default is None:
            raise error
    return default


def str2bool(item: str) -> bool:
    """Convert string to bool. Every string except of `False` and
    `false` are converted to True.

    >>> str2bool('True')
    True
    >>> str2bool('False')
    False
    >>> str2bool('false')
    False
    >>> str2bool('abc')
    True
    >>> str2bool(True)
    True
    >>> str2bool(False)
    False
    """
    return str(item).lower() != 'false'


def simplify(item, not_none: bool = True, removes: set = None):
    if isinstance(item, enum.Enum):
        return item.value
    if isinstance(item, list):
        return [simplify(it, not_none=not_none, removes=removes) for it in item]
    if isinstance(item, tuple):
        raw = [simplify(it, not_none=not_none, removes=removes) for it in item]
        return tuple(raw)
    try:
        item = vars(item)
    except TypeError:
        return item
    for key, value in item.items():
        item[key] = simplify(value, not_none=not_none, removes=removes)
    if not_none:
        item = utila.notnone(item)
    if removes:
        item = utila.removekeys(item, keys=removes)
    return item


def parse_numbers(text, maxcount=None) -> list:
    """\
    >>> parse_numbers('Helmut')
    []
    >>> parse_numbers('This is 1 number an 50 apple')
    [1, 50]
    >>> parse_numbers('133 134 135', maxcount=2)
    [133, 134]
    """
    result = []
    for number in re.findall(r'\d+', text):
        result.append(int(number))
    if maxcount is None:
        return result
    return result[0:maxcount]
