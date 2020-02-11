# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def test_math_isascending():
    items = [0.0, 1, 3.05, 10]
    assert utila.isascending(items)


def test_math_isascending_negative():
    items = [10, 0.5, 5]
    assert utila.isascending(items) is False
