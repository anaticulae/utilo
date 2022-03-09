# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


def rgb2int(red, green, blue) -> int:
    """\
    >>> rgb2int(255, 255, 255)
    16777215
    >>> int2rgb(rgb2int(244, 25, 139))
    (244, 25, 139)
    """
    return red << 16 | green << 8 | blue


def int2rgb(value) -> tuple:
    """\
    >>> int2rgb(16777215)
    (255, 255, 255)
    """
    return (
        255 & value >> 16,
        255 & value >> 8,
        255 & value,
    )
