# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import statistics
import typing

# default number of digits to round
NDIGITS = 2

Number = typing.TypeVar('Number', int, float)  # pylint:disable=C0103
Numbers = typing.List[Number]  # pylint:disable=C0103


def roundme(*items: float, digits: int = NDIGITS) -> float:
    """Round `items` to `NDIGITS.

    It is possible to pass a list of floats or a single float. If a list
    is passed a rounded list is returned. If a single float or a one
    sized list is passed a single rounded float is returned.

    Args:
        items: list of floats or a single float
        digits(int): amout of numbers after dot
    Returns:
        List of round `items` or a single rounded item.
    """
    assert digits >= 0, f'negative digits {digits}'
    result = [round(item, digits) for item in items]
    if len(result) == 1:
        return result[0]
    return result


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


def isascending(items: Numbers) -> bool:
    """Check that `items` are ascending numbers."""
    items = [int(item) for item in items]
    diff = [
        (after - current) for (current, after) in zip(items[:-1], items[1:])
    ]
    return all([item >= 0 for item in diff])


def modes(data: Numbers, minimize: bool = True) -> Number:
    """Return the most common data point from discrete or nominal data.

    It is possible to have multiple common data points. To extract a
    unique point `minimize` enables to decide which number is used.

    See: statistics.mode

    Args:
        data: list of numbers
        minimize(bool): if True the biggest common number is used, if
                        not the smallest is used.
    Raises:
        StatisticsError: if data is empty
    Returns:
        Most common number.
    """
    if not data:
        raise statistics.StatisticsError('no mode for empty data')
    table = statistics._counts(data)  # pylint:disable=W0212
    if len(table) == 1:
        return table[0][0]
    current = sorted([item[0] for item in table])
    if minimize:
        return current[0]
    return current[-1]
