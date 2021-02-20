# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math

import utila

NEAR_ZERO = 0.0000001
NEAR_INF = 10.0**64


def iszero(item: float, diff: float = NEAR_ZERO) -> bool:
    """Check if `item` is near zero.

    >>> iszero(0.000000001)
    True
    """
    return math.fabs(item) <= diff


def isinf(item: float) -> bool:
    """Check if `item` is near inf.

    >>> isinf(10**104)
    True
    """
    return math.fabs(item) >= NEAR_INF


def isequal(first: float, second: float) -> bool:
    # TODO: CONST PACKAGE IS NOT THE RIGHT PLACE
    return utila.near(first, second, diff=NEAR_ZERO)
