# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utila


def test_likelihood_uniform_result_list():
    items = [10, 20, 20, 50]

    result = utila.uniform_result(items)
    expected = [0.1, 0.2, 0.2, 0.5]

    assert result == expected


def test_likelihood_uniform_result_dict():
    items = {
        'A': 100,
        'B': 20,
        'C': 20,
        'D': 60,
    }
    expected = {
        'A': 0.5,
        'B': 0.1,
        'C': 0.1,
        'D': 0.3,
    }
    result = utila.uniform_result(items)

    assert result == expected


@pytest.mark.parametrize('items', [
    [0, 0, 0],
    [],
    {
        'AAA': 0,
        'CDC': 0
    },
])
def test_likelihood_uniform_result_none(items):
    result = utila.uniform_result(items)
    assert result is None


@pytest.mark.parametrize('items, expected', [
    ([0, 20, 20, 20, 15, 10], [20, 20, 20]),
    ([0, 20, 15, 10], 20),
    (
        {
            'A': 100,
            'B': 20,
            'C': 20,
            'D': 60,
        },
        {
            'A': 0.5
        },
    ),
    ([0, 0, 0], None),
    ({
        'A': 0,
        'B': 0,
    }, None),
])
def test_likelihood_maxi(items, expected):
    maximized = utila.maxi(items)
    assert maximized == expected


@pytest.mark.parametrize('items, expected', [
    ([0, 20, 20, 20, 15, 10], 0),
    ([20, 10, 10], [10, 10]),
    (
        {
            'A': 100,
            'B': 20,
            'C': 20,
            'D': 60,
        },
        {
            'B': 0.1,
            'C': 0.1,
        },
    ),
])
def test_likelihood_mini(items, expected):
    minimized = utila.mini(items)
    assert minimized == expected
