# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import typing

# default number of digits to round
NDIGITS = 2

Number = typing.TypeVar('Number', int, float)  # pylint:disable=C0103
Numbers = typing.List[Number]  # pylint:disable=C0103


def roundme(value: float, digits: int = NDIGITS) -> float:
    """Round `value` to `NDIGITS`=2

    Args:
        value(float): value to round
        digits(int): amout of numbers after dot
    Returns:
        rounded `value`
    """
    return round(value, digits)


def numbers(items: typing.List) -> typing.List[int]:
    """Convert iterable `items` to list of int's. Replace none
    convertable items to `None`.

    Args:
        items: iterable with items to convert
    Returns:
        List of int's or None's.
    """
    result = []
    for item in items:
        try:
            result.append(int(item))
        except ValueError:
            result.append(None)
    return result
