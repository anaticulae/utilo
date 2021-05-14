# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os

import utila


def file_line_length(path: str) -> int:
    """Count number of lines of given `path`.

    >>> file_line_length(__file__) >= 10
    True
    """
    return len(utila.file_read(path).splitlines())


def isfilepath(path: str) -> bool:
    """Check that given `path` is a file path.

    >>> isfilepath('/c/tmp/file.txt')
    True
    >>> isfilepath('/c/tmp/.tmp')
    False
    """
    assert path, path
    if os.path.exists(path):
        return os.path.isfile(path)
    base = os.path.basename(path)
    if base[0] == '.':
        # .tmp
        return False
    return '.' in base
