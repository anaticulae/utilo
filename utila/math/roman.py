# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib

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


def roman(*items) -> str:
    """Converts Arabic numbers to Roman numbers.

    >>> roman(5)
    'V'
    >>> roman(1, 5, 6, 10)
    ['I', 'V', 'VI', 'X']
    """
    reverse = {value: key for key, value in NUMBERS.items()}
    result = [reverse[item] for item in items]
    if len(result) == 1:
        return result[0]
    return result


def arabic(*items) -> int:
    """Converst Roman to Arabic numbers.

    >>> arabic('XII')
    12
    >>> arabic('I', 'IIII', 'VI', 'VIIII')
    [1, 4, 6, 9]
    """
    result = []
    for item in items:
        item = str(item).upper()
        try:
            result.append(NUMBERS[item])
        except KeyError:
            result.append(EXCEPTION[item])
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
    """
    with contextlib.suppress(KeyError):
        _ = arabic(item)
        return True
    return False


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
