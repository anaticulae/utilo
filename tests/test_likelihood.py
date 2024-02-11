# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Test likelihood methods:

    - maxi
    - mini
    - uniform_result

"""
import pytest

import utila


def test_likelihood_uniform_result_list():
    """Determine uniformed occurrence of item in `list` collection."""
    items = [10, 20, 20, 50]

    result = utila.uniform_result(items)
    expected = [0.1, 0.2, 0.2, 0.5]

    assert result == expected


def test_likelihood_uniform_result_dict():
    """Determine uniformed occurrence of item in `dict` collection."""
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
    """Run uniformation with expected empty result, because input has no
    numbers."""
    result = utila.uniform_result(items)
    assert result is None


@pytest.mark.parametrize('items, expected', [
    ([0, 20, 20, 20, 15, 10], [20, 20, 20]),
    ([0, 20, 15, 10], [20]),
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
    """Test to extract maximized feature for `list` and `dict` example.
    If there are more than one minimal items, all are returned."""
    maximized = utila.maxi(items, count=3)
    assert maximized == expected


@pytest.mark.parametrize('items, expected', [
    ([0, 20, 20, 20, 15, 10], [0]),
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
    """Test to extract minimized feature for `list` and `dict` example.
    If there are more than one minimal items, all are returned."""
    minimized = utila.mini(items, count=2)
    assert minimized == expected
