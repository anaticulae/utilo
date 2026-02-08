# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import statistics

import pytest

import utilo


def test_math_isascending():
    items = [0.0, 1, 3.05, 10]
    assert utilo.isascending(items)


def test_math_isascending_negative():
    items = [10, 0.5, 5]
    assert not utilo.isascending(items)


@pytest.mark.parametrize('value, digits, expected', [
    (0.9, 0, 1.0),
    (0.9, 1, 0.9),
    (0.993, 2, 0.99),
    ([1.1, 2.5, 3.0], 0, [1.0, 2.0, 3.0]),
    ([1.1, 2.5, 3.0], 1, [1.1, 2.5, 3.0]),
])
def test_roundme(value, digits, expected):
    if isinstance(value, list):  # pylint:disable=W0160
        result = utilo.roundme(*value, digits=digits)
    else:
        result = utilo.roundme(value, digits=digits)
    assert result == expected


def test_roundme_single():
    rounded = utilo.roundme(1.558, 2.448)
    assert rounded == [1.56, 2.45], str(rounded)


def test_roundme_single_with_digits():
    rounded = utilo.roundme(1.558, 2.448, digits=1)
    assert rounded == [1.6, 2.4], str(rounded)


def test_math_roundme_tuple_vs_list():
    fixed = (1, 2, 3, 4)
    variable = [1, 2, 3, 4]

    assert utilo.roundme(fixed) == fixed
    assert utilo.roundme(variable) == variable
    assert utilo.roundme(*variable) == variable
    assert utilo.roundme(*fixed) == variable


def test_math_roundme_str_error():
    with pytest.raises(ValueError):
        utilo.roundme('h')
        utilo.roundme('hello')


def test_modes():
    assert utilo.modes((1, 1, 1, 3, 3, 3)) == [1, 3]
    assert utilo.modes((1, 1, 3)) == 1


def test_modes_empty():
    with pytest.raises(statistics.StatisticsError):
        utilo.modes([])
