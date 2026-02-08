# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import dataclasses

import utilo


def test_simplify():
    """Convert object to python basic data structures."""
    example = utilo.FeaturePackConfig()
    simple = utilo.simplify(example)
    assert 'prefixflag' in simple


@dataclasses.dataclass
class Human:
    name: str = None
    year: int = None


def test_simplify_dataclass():
    data = Human('Helm', 1920)
    before = hash(str(data))
    simple = utilo.simplify(data)
    assert simple
    assert hash(str(data)) == before, 'do not change data while simplify'
