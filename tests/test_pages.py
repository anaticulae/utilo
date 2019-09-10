# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from pytest import mark

from utila import pages
from utila import should_skip

EMPTY_TUPLE = tuple([])

MAX_PAGES = 100


@mark.parametrize('pattern, expected', [
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
    result = pages(pattern, pagecount=MAX_PAGES)
    assert result == expected, str(result)


def test_utils_should_skip():
    assert should_skip(5, (1, 2, 3)) is True
    assert should_skip(5, (1, 2, 3, 5)) is False
    assert should_skip(5, None) is False
