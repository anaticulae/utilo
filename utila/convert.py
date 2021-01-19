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


def simplify(item):
    if isinstance(item, enum.Enum):
        return item.value
    if isinstance(item, list):
        return [simplify(it) for it in item]
    if isinstance(item, tuple):
        return tuple([simplify(it) for it in item])
    try:
        item = vars(item)
    except TypeError:
        return item
    for key, value in item.items():
        item[key] = simplify(value)
    return item


def parse_numbers(text):
    """\
    >>> parse_numbers('Helmut')
    []
    >>> parse_numbers('This is 1 number an 50 apple')
    [1, 50]
    """
    result = []
    for number in re.findall(r'\d+', text):
        result.append(int(number))
    return result
