# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib

import utila

NUMBERS = {
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4,
    'V': 5,
    'VI': 6,
    'VII': 7,
    'VIII': 8,
    'IX': 9,
    'X': 10,
    'XI': 11,
    'XII': 12,
    'XIII': 13,
    'XIV': 14,
    'XV': 15,
    'XVI': 16,
    'XVII': 17,
    'XVIII': 18,
    'XIX': 19,
    'XX': 20,
    'XXI': 21,
    'XXII': 22,
    'XXIII': 23,
    'XXIV': 24,
    'XXV': 25,
    'XXVI': 26,
    'XXVII': 27,
    'XXVIII': 28,
    'XXIX': 29,
    'XXX': 30,
    'XXXI': 31,
    'XXXII': 32,
    'XXXIII': 33,
    'XXXIV': 34,
    'XXXV': 35,
    'XXXVI': 36,
    'XXXVII': 37,
    'XXXVIII': 38,
    'XXXIX': 39,
    'XL': 40,
}

EXCEPTION = {
    'VIIII': 9,
    'IIII': 4,
    'XIIII': 14,
    'XXVIIII': 29,
    'XXXIIII': 34,
    'XXXVIIII': 39,
}

NUMBERS_REVERSE = utila.dict_reverse(NUMBERS)


def roman(*items) -> str:
    """Converts Arabic numbers to Roman numbers.

    >>> roman(5)
    'V'
    >>> roman(1, 5, 6, 10)
    ['I', 'V', 'VI', 'X']
    >>> roman(-1, 0, 1)
    Traceback (most recent call last):
        ...
    ValueError: greater than zero required: (-1, 0, 1)
    """
    if any(item for item in items if item <= 0):
        raise ValueError(f'greater than zero required: {items}')
    result = [NUMBERS_REVERSE[item] for item in items]
    if len(result) == 1:
        return result[0]
    return result


def arabic(*items) -> int:
    """Converts Roman to Arabic numbers.

    >>> arabic('XII')
    12
    >>> arabic('I', 'IIII', 'VI', 'VIIII')
    [1, 4, 6, 9]
    """
    result = []
    for item in items:
        item = str(item).upper()
        # make converter robust against white space inside
        item = item.replace(' ', '', 1)
        with contextlib.suppress(KeyError):
            result.append(NUMBERS[item])
            continue
        try:
            result.append(EXCEPTION[item])
        except KeyError:
            return None
    if len(result) == 1:
        return result[0]
    return result


def isroman(item) -> bool:
    """\
    >>> isroman('XII')
    True
    >>> isroman('10')
    False
    >>> isroman(10)
    False
    >>> isroman('XX II')  # roman number with space inside
    True
    >>> isroman('ABC')
    False
    """
    if arabic(item) is None:
        return False
    return True


def isarabic(item) -> bool:
    """\
    >>> isarabic('10')
    True
    >>> isarabic(1.1)
    False
    >>> isarabic('1.1')
    False
    >>> isarabic('Ten')
    False
    """
    if isinstance(item, float):
        return False
    with contextlib.suppress(ValueError):
        _ = int(item)
        return True
    return False


def pagenumber(item: str) -> int:
    """\
    >>> pagenumber('XII')
    12
    >>> pagenumber('191')
    191
    >>> pagenumber('AGC')
    Traceback (most recent call last):
        ...
    ValueError: invalid page number: AGC
    """
    if isarabic(item):
        return int(item)
    if isroman(item):
        return arabic(item)
    raise ValueError(f'invalid page number: {item}')


def pagenumber_plus(item: str) -> str:
    """\
    >>> pagenumber_plus(12)
    '13'
    """
    number = pagenumber(item) + 1
    if isarabic(item):
        return str(number)
    if isroman(item):
        return roman(number)
    raise ValueError(f'invalid page number: {item}')


def pagenumber_minus(item: str) -> str:
    """\
    >>> pagenumber_minus('X')
    'IX'
    """
    number = pagenumber(item) - 1
    if isarabic(item):
        return str(number)
    if isroman(item):
        return roman(number)
    raise ValueError(f'invalid page number: {item}')
