# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

NDIGITS = 2


def roundme(value: float, digits: int = NDIGITS) -> float:
    """Round `value` to `NDIGITS`=2

    Args:
        value(float): value to round
        digits(int): amout of numbers after dot
    Returns:
        rounded `value`
    """
    return round(value, digits)
