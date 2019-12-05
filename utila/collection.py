# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import typing


def make_unique(items) -> typing.List[str]:
    """Convert collection where every element exists only once.

    Hint:
        stable algorithm which holds the previous order
    """
    result = []
    for item in items:
        if item in result:
            continue
        result.append(item)
    return result
