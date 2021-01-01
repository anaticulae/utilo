# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
import utila


def test_collection_make_unique():
    assert utila.make_unique(['a', 'b', 'c', 'd', 'a']) == ['a', 'b', 'c', 'd']
    assert utila.make_unique([1, 2, 3, 1, 2, 3]) == [1, 2, 3]


def test_single_contains():
    single = utila.Single()
    assert not single.contains(10)
    assert single.contains(10)


def test_single_contains_unhashable():
    """Support unhashable items."""
    single = utila.Single()
    assert not single.contains(set())
    assert single.contains(set())
