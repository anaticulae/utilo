# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import typing


def work() -> typing.List[typing.Tuple[str, bytes]]:
    result = [
        ('imageinfo', '\x00\xff'),
        ('second', '\x12\xff'),
    ]
    return result
