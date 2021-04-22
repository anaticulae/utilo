# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def file_read_lines(path: str, start: int = None, end: int = None) -> str:
    """\
    >>> len(file_read_lines(__file__).splitlines()) > 20
    True
    >>> len(file_read_lines(__file__, 5, 6).splitlines())
    1
    """
    data = utila.file_read(path)
    splitted = data.splitlines(keepends=True)
    start = start or 0
    end = end or len(splitted)
    result = ''.join(splitted[start:end])
    return result
