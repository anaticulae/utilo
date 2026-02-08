# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import collections

import pytest
import texmex

import utilo

MAX_PAGES = 100

MinimalPage = collections.namedtuple('MinimalPage', 'page')


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
    result = utilo.parse_pages(pattern, pagecount=MAX_PAGES)
    assert result == expected, str(result)


def test_pages_should_skip():
    assert utilo.should_skip(5, (1, 2, 3))
    assert not utilo.should_skip(5, (1, 2, 3, 5))
    assert not utilo.should_skip(5, None)


@pytest.fixture
def minimal_pages():
    pages = [MinimalPage(0), MinimalPage(1), MinimalPage(2), MinimalPage(4)]
    return pages


def test_pages_select_page(minimal_pages):  # pylint:disable=W0621
    assert utilo.select_page(minimal_pages, 4) == MinimalPage(4)


def test_pages_select_pages(minimal_pages):  # pylint:disable=W0621
    expect_sorted = [MinimalPage(1), MinimalPage(4)]
    assert utilo.select_pages(minimal_pages, (4, 1)) == expect_sorted


def test_pages_select_page_invalid(minimal_pages):  # pylint:disable=W0621
    none = utilo.select_page(minimal_pages, 10)
    assert none is None, none


def test_pages_select_page_duplicated_source():
    pages = [MinimalPage(0), MinimalPage(0), MinimalPage(0), MinimalPage(4)]
    with pytest.raises(ValueError):
        utilo.select_page(pages, 0)


def test_page_select_page_none():
    with pytest.raises(ValueError):
        utilo.select_page(None, 0)


MiniPageContent = collections.namedtuple('MiniPageContent', 'page, content')

EXAMPLE = [
    [
        MiniPageContent(0, 'zero'),
        MiniPageContent(2, 'zwei'),
        MiniPageContent(5, 'fuenf'),
    ],
    [
        MiniPageContent(0, 'zero'),
        MiniPageContent(1, 'eins'),
        MiniPageContent(3, 'drei'),
        MiniPageContent(4, 0),
    ],
    [
        MiniPageContent(5, 'fuenf'),
    ],
]

EXPECTED = [
    (0, (MiniPageContent(0, 'zero'), MiniPageContent(0, 'zero'), None)),
    (1, (None, MiniPageContent(1, 'eins'), None)),
    (2, (MiniPageContent(2, 'zwei'), None, None)),
    (3, (None, MiniPageContent(3, 'drei'), None)),
    (4, (None, MiniPageContent(4, 0), None)),
    (5, (MiniPageContent(5, 'fuenf'), None, MiniPageContent(5, 'fuenf'))),
]


def test_sync_pages_iterator():
    synced = list(utilo.sync_pages(EXAMPLE))
    assert synced == EXPECTED


DOUBLE_EMPTY = [
    [
        MiniPageContent(0, 'zero'),
        MiniPageContent(2, 'zwei'),
        MiniPageContent(5, 'fuenf'),
    ],
    [],
]

DOUBLE_EXPECTED = [
    (0, (MiniPageContent(page=0, content='zero'), None)),
    (2, (MiniPageContent(page=2, content='zwei'), None)),
    (5, (MiniPageContent(page=5, content='fuenf'), None)),
]


def test_sync_double_empty():
    synced = list(utilo.sync_pages(
        DOUBLE_EMPTY,
        default=None,
    ))
    assert synced == DOUBLE_EXPECTED


DOUBLE_LIST_EXPECTED = [
    (0, (MiniPageContent(page=0, content='zero'), [])),
    (2, (MiniPageContent(page=2, content='zwei'), [])),
    (5, (MiniPageContent(page=5, content='fuenf'), [])),
]


def test_sync_double_list():
    synced = list(utilo.sync_pages(
        DOUBLE_EMPTY,
        default=[],
    ))
    assert synced == DOUBLE_LIST_EXPECTED


PTNS = [
    [
        texmex.PTN(page=0),
        texmex.PTN(page=1),
        texmex.PTN(page=2),
        texmex.PTN(page=4),
    ],
    [],
]
PTNS_EXPECTED = [
    (0, (texmex.PTN(page=0), [])),
    (1, (texmex.PTN(page=1), [])),
    (2, (texmex.PTN(page=2), [])),
    (4, (texmex.PTN(page=4), [])),
]


def test_sync_ptns():
    synced = list(utilo.sync_pages(
        PTNS,
        default=[],
    ))
    assert synced == PTNS_EXPECTED
