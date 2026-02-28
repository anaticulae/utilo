# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest
import utilotest

import utilo


@pytest.mark.parametrize('first, second, expected', [
    pytest.param((0, 0, 10, 10), (0, 10, 10, 0), (5.0, 5.0), id='middlematch'),
    pytest.param((0, 0, 10, 10), (0, 10, 5, 10), None, id='nomatch'),
    pytest.param((0, 0, 10, 0), (0, 5, 10, 5), None, id='nomatch_horizontal'),
    pytest.param((0, 10, 10, 10), (5, 5, 5, 10), (5, 10), id='m_inf'),
    pytest.param((10, 10, 0, 10), (5, 10, 5, 5), (5, 10), id='m_inf_switched'),
])
def test_math_intersecting_lines(first, second, expected):
    match = utilo.intersecting_lines(first, second)
    assert match == expected, match


@pytest.mark.parametrize('first, second', [
    pytest.param((10, 10, 5, 10), (10, 10, 10, 10), id='dot'),
    pytest.param((0, 0, 10, 10), (0, 0, 10, 10), id='identical'),
])
def test_math_intersecting_line_invalid_input(first, second):
    with pytest.raises(ValueError):
        utilo.intersecting_lines(first, second)


def test_math_intersecting_line_with_offset():
    first = (479.71, 755.4, 479.71, 767.36)
    second = (479.71, 743.05, 479.71, 755.0)

    with_error = utilo.intersecting_lines(first, second, max_diff=5.0)
    assert with_error


@utilotest.no_cov
@utilotest.longrun
def test_intersecting_timeit(lines):
    """Measure intersecting line times."""
    for first, second in zip(lines[0::2], lines[1::2]):
        utilo.intersecting_lines(first, second)
