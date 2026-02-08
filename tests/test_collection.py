# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utilo


def test_collection_make_unique():
    assert utilo.make_unique(['a', 'b', 'c', 'd', 'a']) == ['a', 'b', 'c', 'd']
    assert utilo.make_unique([1, 2, 3, 1, 2, 3]) == [1, 2, 3]


def test_single_contains():
    single = utilo.Single()
    assert not single.contains(10)
    assert single.contains(10)


def test_single_contains_unhashable():
    """Support unhashable items."""
    single = utilo.Single()
    assert not single.contains(set())
    assert single.contains(set())


def test_single_equal_hash():
    assert hash(-2) == hash(-1)

    single = utilo.Single()
    assert not single.contains(-2)
    assert not single.contains(-1)
    assert single.contains(-2)
    assert single.contains(-1)
