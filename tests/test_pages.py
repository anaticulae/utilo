# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections

import pytest

import utila

MAX_PAGES = 100



@pytest.mark.parametrize('pattern, expected', [
    (' :  ', None),
    ('0:0', None),
    ('50:', tuple(range(50, MAX_PAGES))),
    ('0:10', tuple(range(0, 10))),
    ('5:5', None),
    ('5:6', tuple(range(5, 6))),
    (':', None),
    ('asdas:', None),
    ('   ', None),
    ('5', (5,)),
    ('0', (0,)),
    ('1,2,3,5,10', (1, 2, 3, 5, 10)),
    ('a,2,d,,10', None),
    ('a,10', None),
])
def test_pages(pattern, expected):
    result = utila.pages(pattern, pagecount=MAX_PAGES)
    assert result == expected, str(result)


def test_pages_should_skip():
    assert utila.should_skip(5, (1, 2, 3)) is True
    assert utila.should_skip(5, (1, 2, 3, 5)) is False
    assert utila.should_skip(5, None) is False
