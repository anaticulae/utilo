# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utila


def linecount(count):
    generator = utila.numbers_random(count=count, mins=0, maxs=768, seed=1.0)
    lines = []
    for _ in range(int(count / 4)):
        lines.append(tuple(next(generator) for _ in range(4)))
    return lines


@pytest.fixture
def lines():
    count = 1024 * 1024 * 4
    return linecount(count)


@pytest.fixture
def thousand_lines():
    count = 1024
    return linecount(count)
