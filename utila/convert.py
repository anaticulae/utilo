# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import dataclasses
import enum
import re
import sys

import utila

DIGITS_FLOAT = sys.float_info.dig


def str2int(item: str, default=None) -> int:
    """\
    >>> str2int('10')
    10
    >>> str2int('1.3')
    1
    >>> str2int('ABC', default=13)
    13
    """
    if len(str(item)) < DIGITS_FLOAT:
        # maximum number of decimal digits that can be faithfully
        # represented in a float;
        item = str2float(item, default=default)
    if item is not None:
        item: int = int(item)
    return item


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


def simplify(item, not_none: bool = True, removes: set = None):  # pylint:disable=R1260
    if dataclasses.is_dataclass(item):
        item = dataclasses.asdict(item)
    if isinstance(item, enum.Enum):
        return item.value
    if isinstance(item, list):
        return [simplify(it, not_none=not_none, removes=removes) for it in item]
    if isinstance(item, tuple):
        raw = [simplify(it, not_none=not_none, removes=removes) for it in item]
        return tuple(raw)
    if not isinstance(item, dict):
        # if item is dict already, no converting is required
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


INTS = re.compile(r'\d+')
FLOATS = re.compile(r'\d+\.\d+')


def parse_ints(text, maxcount=None) -> list:
    """\
    >>> parse_ints('Helmut')
    []
    >>> parse_ints('This is 1 number an 50 apple')
    [1, 50]
    >>> parse_ints('133 134 135', maxcount=2)
    [133, 134]
    """
    result = []
    for number in INTS.findall(text):
        result.append(int(number))
    if maxcount is None:
        return result
    return result[0:maxcount]


def parse_floats(text, maxcount=None) -> list:
    """\
    >>> parse_floats('Helmut')
    []
    >>> parse_floats('This is 1.0 number an 50.345345345 apple')
    [1.0, 50.345345345]
    >>> parse_floats('2.2 3.5 3.7', maxcount=2)
    [2.2, 3.5]
    """
    result = []
    for number in FLOATS.findall(text):
        result.append(float(number))
    if maxcount is None:
        return result
    return result[0:maxcount]


ON = 'TRUE 1 ON'.split()


def parse_state(state: str) -> bool:
    """\
    >>> parse_state('ON')
    True
    >>> parse_state('True')
    True
    >>> parse_state(' 1 ')
    True
    >>> parse_state('off')
    False
    >>> parse_state('false')
    False
    >>> parse_state('0')
    False
    >>> parse_state(None)
    False
    """
    state = str(state).strip().upper()
    return state in ON
