# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import math


def norm(x0, y0, x1, y1) -> float:
    """Determine `norm` distance.

    >>> norm(*(100,100,200,200))
    141.42...
    """
    return math.sqrt(pow(x1 - x0, 2) + pow(y1 - y0, 2))


def manhatten(x0, y0, x1, y1) -> float:
    """Determine manhatten distance.

    >>> manhatten(*(10,10,25,25))
    30
    """
    assert x0 <= x1, f'{x0}<={x1}'
    assert y0 <= y1, f'{y0}<={y1}'
    return (x1 - x0) + (y1 - y0)
