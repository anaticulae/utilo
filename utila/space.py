# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""PDF Coordinate Converter
====================

Millimeter to points
--------------------

>>> points(210, 297) # DINA4
(595.28, 841.89)

Points to millimeter
--------------------

>>> millimeters(595, 841)
(209.9, 296.69)

DIN-SIZES
---------

A3 = (297, 420)
A4 = (210, 297)
A5 = (148, 210)
A6 = (104, 148)
"""

import utila

INC_TO_MILI = 25.4  # millimeter
PT = 1 / 72


def millimeter(point: float, *, userunit=1.0, digits: int = 2) -> float:  # pylint:disable=W0621
    """Convert pdf user unit space to millimeter.

    See 7.7.3.3 PageObjects

    >>> millimeter(595) # DINA4-width 210mmm
    209.9
    >>> millimeter(595, userunit=2.0)
    419.81
    """
    assert userunit >= 1.0, userunit
    userpoints = PT * userunit
    inc = point * userpoints
    mili = inc * INC_TO_MILI
    rounded = utila.roundme(mili, digits=digits)
    return rounded


def millimeters(  # pylint:disable=W0621
    *points: utila.Numbers,
    userunit=1.0,
    digits: int = 2,
) -> utila.Numbers:
    result = [
        millimeter(item, userunit=userunit, digits=digits) for item in points
    ]
    return tuple(result)


def point(millimeter: float, *, userunit=1.0, digits: int = 2) -> float:  # pylint:disable=W0621
    """Convert millimeter to internal pt/points.

    >>> point(25.4)
    72.0
    """
    assert userunit >= 1.0, userunit
    inc = millimeter / INC_TO_MILI
    point_ = inc / PT / userunit
    rounded = utila.roundme(point_, digits=digits)
    return rounded


def points(  # pylint:disable=W0621
    *millimeters: utila.Numbers,
    userunit=1.0,
    digits: int = 2,
) -> utila.Numbers:
    result = [
        point(item, userunit=userunit, digits=digits) for item in millimeters
    ]
    return tuple(result)


def inch(point: float, userspace: float = 1.0) -> float:  # pylint:disable=W0621
    """\
    >>> inch(72)
    1.0
    """
    scale = 72.0 / userspace
    result = point / scale
    return result
