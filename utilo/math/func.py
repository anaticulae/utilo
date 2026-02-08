# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

import utilo


def ranged_exp(
    mini: float,
    maxi: float,
    steps: int = 15,
    digits: int = 2,
    func=None,
):
    """Determine numbers between `mini` and `maxi`.

    >>> utilo.ranged_exp(0.1, 100, steps=10)
    [0.1, 0.12, 0.18, 0.34, 0.76, 1.92, 5.06, 13.61, 36.84, 99.99]
    >>> utilo.ranged_exp(0.1, 20, steps=5)
    [0.1, 0.73, 2.43, 7.06, 19.64]
    """
    func = func if func else math.exp
    maxed = func(steps - 1) / (maxi - mini)
    result = []
    for index in range(steps):
        value = mini + (func(index) - 1) / maxed
        value = utilo.roundme(value, digits=digits)
        result.append(value)
    return result
