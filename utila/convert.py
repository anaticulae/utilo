# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


def str2int(item: str) -> int:
    """\
    >>> str2int('10')
    10
    >>> str2int('1.3')
    1
    """
    return int(float(item))


def str2bool(item: str) -> bool:
    """Convert string to bool. Every string except of `False` and
    `false` are converted to True.

    >>> str2bool('True')
    True
    >>> str2bool('False')
    False
    >>> str2bool('false')
    False
    >>> str2bool('abc')
    True
    >>> str2bool(True)
    True
    >>> str2bool(False)
    False
    """
    return str(item).lower() != 'false'
