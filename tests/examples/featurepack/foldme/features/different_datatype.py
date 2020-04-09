# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================


def work(directory) -> list:  # pylint:disable=W0613
    result = []
    result.append(('first', 'txt'))
    result.append(('second', 'fdp'))
    result.append((b'\x00\x11\x22', 'png'))
    return result
